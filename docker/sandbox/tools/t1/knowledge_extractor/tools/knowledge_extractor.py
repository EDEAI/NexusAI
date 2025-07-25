import json
from collections.abc import Generator
from typing import Any, Optional

from dify_plugin import Tool
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.model.message import UserPromptMessage
from dify_plugin.entities.tool import ToolInvokeMessage

from splitter.fixed_text_splitter import FixedRecursiveCharacterTextSplitter
from tools.prompts import EXTRACT_KNOWLEDGE_PROMPT, OUTPUT_STRUCTURE, ANALYZE_KNOWLEDGE_PROMPT


class KnowledgeExtractorTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        model_config = tool_parameters.get('model')
        if not model_config:
            raise ValueError("Please select the model")
        text = tool_parameters.get('text')
        if not text:
            raise ValueError("Please fill in the text")
        instruction = tool_parameters.get('instruction', None)
        language = tool_parameters.get('language')
        if not language:
            raise ValueError("Please select the language")
        chunk_size = tool_parameters.get('chunk_size', 8192)
        chunk_overlap = tool_parameters.get('chunk_overlap', 0)
        separator = tool_parameters.get('separator', "\\s*(?>\\R)\\s*(?>\\R)\\s*")

        output = self._invoke_extract_knowledge(
            model_config=model_config,
            text=text,
            instruction=instruction,
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator)

        yield self.create_text_message(output)

    def _invoke_extract_knowledge(self,
                                  model_config: LLMModelConfig | dict,
                                  text: str,
                                  instruction: str = None,
                                  language: str = "English",
                                  chunk_size: int = 8192,
                                  chunk_overlap: int = 0,
                                  separator: str = "\\s*(?>\\R)\\s*(?>\\R)\\s*",
                                  ) -> str:
        """
        Extract knowledge.
        """

        splitter = FixedRecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            fixed_separator=separator,
            separators=["\n\n", "。", ". ", " ", ""],
        )
        texts = splitter.split_text(text=text)

        knowledges = []
        for text in texts:
            prompt_messages = [
                UserPromptMessage(
                    content=EXTRACT_KNOWLEDGE_PROMPT.format(
                        instruction=instruction,
                        output_structure=json.dumps(OUTPUT_STRUCTURE),
                        text=text,
                        language=language,
                    )
                )
            ]
            response = self.session.model.llm.invoke(
                model_config=model_config,
                prompt_messages=prompt_messages,
                stream=False
            )
            json_response = self._extract_complete_json_response(response.message.content)
            if json_response is None:
                continue
            if isinstance(json_response, dict):
                if 'has_content' in json_response and json_response['has_content'] is True:
                    knowledge = json_response['knowledge']
                    knowledges.extend(knowledge if isinstance(knowledge, list) else [knowledge])

        if len(knowledges) == 0:
            return ""

        output = self._invoke_analyze_knowledge(
            model_config=model_config,
            text="\n\n".join(knowledges),
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator,
        )
        return output

    def _invoke_analyze_knowledge(self,
                                  model_config: LLMModelConfig | dict,
                                  text: str,
                                  instruction: str = None,
                                  language: str = "English",
                                  chunk_size: int = 8192,
                                  chunk_overlap: int = 0,
                                  separator: str = "\\s*(?>\\R)\\s*(?>\\R)\\s*",
                                  ) -> str:
        """
        Recursive Analyze knowledge.
        """

        splitter = FixedRecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            fixed_separator=separator,
            separators=["\n\n", "。", ". ", " ", ""],
        )
        texts = splitter.split_text(text=text)

        analyzes = []
        for text in texts:
            prompt_messages = [
                UserPromptMessage(
                    content=ANALYZE_KNOWLEDGE_PROMPT.format(
                        instruction=instruction,
                        content=text,
                        language=language,
                    )
                )
            ]
            response = self.session.model.llm.invoke(
                model_config=model_config,
                prompt_messages=prompt_messages,
                stream=False
            )
            analyzes.append(response.message.content)

        if len(analyzes) == 1:
            return analyzes[0]

        return self._invoke_analyze_knowledge(
            model_config=model_config,
            text="\n\n".join(analyzes),
            instruction=instruction,
            language=language,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separator=separator,
        )

    @staticmethod
    def _extract_complete_json_response(result: str) -> Optional[dict | list[dict]]:
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
                        return json.loads(json_str)
                    except Exception:
                        pass
