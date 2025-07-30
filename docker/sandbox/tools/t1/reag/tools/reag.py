from collections.abc import Generator, AsyncGenerator
from typing import Any, Optional, cast
import tempfile
import os
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from dify_plugin import Tool # type: ignore
from dify_plugin.entities.tool import ToolInvokeMessage # type: ignore
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage # type: ignore
from dify_plugin.entities.model.llm import LLMModelConfig # type: ignore

from markitdown import MarkItDown # type: ignore
from pydantic import BaseModel # type: ignore
import asyncio
from .prompt import REAG_SYSTEM_PROMPT


class Document(BaseModel):
    name: str
    content: str

class QueryResult(BaseModel):
    content: str
    reasoning: str
    is_irrelevant: bool
    document: Document

class ReagTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        files = tool_parameters.get('files', [])
        query = tool_parameters.get('query')
        documents = []

        for file in files:
            try:
                file_extension = file.extension if file.extension else '.tmp'
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                    temp_file.write(file.blob)
                    temp_file_path = temp_file.name
                
                try:
                    md = MarkItDown()
                    result = md.convert(temp_file_path)
                    if result and hasattr(result, 'text_content'):
                        document = Document(
                            name=file.filename,
                            content=result.text_content
                        )
                        documents.append(document)
                    if result and hasattr(result, 'text_content'):
                        pass
                    else:
                        error_msg = f"Conversion failed. Result: {result}"
                        yield self.create_text_message(text=error_msg)
                finally:
                    if os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
            
            except Exception as e:
                error_msg = f"Error processing file: {str(e)}"
                yield self.create_text_message(text=error_msg)

        # 添加计数器
        self.invoke_count = getattr(self, 'invoke_count', 0)
        
        # 如果有文档和查询，进行文档查询
        if documents and query:
            def process_single_document(document):
                try:
                    # 增加计数
                    self.invoke_count += 1
                    print(f"LLM Invoke count: {self.invoke_count}")
                    
                    response = self.session.model.llm.invoke(
                        model_config=LLMModelConfig(
                            provider=tool_parameters.get('model', {}).get('provider'),
                            model=tool_parameters.get('model', {}).get('model'),
                            mode=tool_parameters.get('model', {}).get('mode')
                        ),
                        prompt_messages=[
                            SystemPromptMessage(
                                content=f'{REAG_SYSTEM_PROMPT}\n\n'
                                       f'# Available source\n\n'
                                       f'Document Name: {document.name}\n'
                                       f'Document Content: {document.content}'
                            ),
                            UserPromptMessage(content=query)
                        ],
                        stream=False
                    )
                    
                    # 确保我们获取到字符串内容
                    result = response.message.content if hasattr(response, 'message') else str(response)
                    
                    # 打印原始 result 内容
                    print(f"\n=== Raw Result for {document.name} ===\n{result}\n===================\n")
                    
                    # 首先尝试提取 think 标签内容
                    think_match = re.search(r'<think>(.*?)</think>', str(result), re.DOTALL)
                    reasoning = think_match.group(1).strip() if think_match else ""
                    
                    # 移除 think 标签后的文本
                    cleaned_text = re.sub(r'<think>.*?</think>', '', str(result), re.DOTALL).strip()
                    
                    # 尝试解析为 JSON
                    json_result = self._extract_complete_json_response(cleaned_text)
                    if json_result:
                        # 检查是否是简单的content-only格式
                        if isinstance(json_result, dict) and len(json_result) == 1 and 'content' in json_result:
                            content = json_result['content']
                            is_irrelevant = False
                        else:
                            content = json_result.get('content', '')
                            is_irrelevant = json_result.get('isIrrelevant', False)
                    else:
                        # 如果不是 JSON，则使用正则表达式匹配
                        irrelevant_match = re.search(r'isIrrelevant:\s*(true|false)', cleaned_text, re.IGNORECASE)
                        is_irrelevant = irrelevant_match.group(1).lower() == 'true' if irrelevant_match else True
                        
                        content_match = re.search(r'\*\*Answer:\*\*\s*(.*?)(?:\n|$)', cleaned_text, re.DOTALL)
                        content = content_match.group(1).strip() if content_match else cleaned_text.strip()
                    
                    query_result = QueryResult(
                        content=content,
                        reasoning=reasoning,
                        is_irrelevant=is_irrelevant,
                        document=document
                    )
                    if not query_result.is_irrelevant:
                        print(f"query_result: {query_result}")
                    
                    return query_result
                
                except Exception as e:
                    error_msg = f"Error processing query result: {str(e)}"
                    return None
            
            with ThreadPoolExecutor(max_workers=len(documents)) as executor:
                future_to_doc = {executor.submit(process_single_document, doc): doc 
                               for doc in documents}
                
                results = []
                for future in as_completed(future_to_doc):
                    result = future.result()
                    if result and not result.is_irrelevant:
                        results.append(result)
                
                print(f"results: {results}")
                if results:
                    # 构建一个包含所有结果的字典
                    valuable_res = [
                        {
                            "content": r.content,
                            "reasoning": r.reasoning,
                            "is_irrelevant": r.is_irrelevant,
                            "document": {
                                "name": r.document.name,
                                "content": r.document.content
                            }
                        } for r in results
                    ]
                    
                    # 使用 create_variable_message 返回结果
                    yield self.create_variable_message("query_results", valuable_res)

    def _extract_complete_json_response(self, result: str) -> Optional[dict]:
        """
        Extract complete json response.
        """

        def extract_json(text):
            """
            From a given JSON started from '{' or '[' extract the complete JSON object.
            """
            stack = []
            for i, c in enumerate(text):
                if c in {"{", "["}:
                    stack.append(c)
                elif c in {"}", "]"}:
                    # check if stack is empty
                    if not stack:
                        return text[:i]
                    # check if the last element in stack is matching
                    if (c == "}" and stack[-1] == "{") or (c == "]" and stack[-1] == "["):
                        stack.pop()
                        if not stack:
                            return text[: i + 1]
                    else:
                        return text[:i]
            return None

        # extract json from the text
        for idx in range(len(result)):
            if result[idx] == "{" or result[idx] == "[":
                json_str = extract_json(result[idx:])
                if json_str:
                    try:
                        return cast(dict, json.loads(json_str))
                    except Exception:
                        pass
        return None