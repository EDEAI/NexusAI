from cmath import e
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.alchemy_db_client import get_db_schema
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.entities.model.message import SystemPromptMessage, UserPromptMessage

from utils.prompt_loader import PromptLoader
from utils.alchemy_db_client import format_schema_dsl

class HologresText2dataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        model_info= tool_parameters.get('model')
        meta_data = get_db_schema(
            db_type=tool_parameters['db_type'],
            host=tool_parameters['host'],
            port=tool_parameters['port'],
            database=tool_parameters['db_name'],
            username=tool_parameters['username'],
            password=tool_parameters['password'],
            table_names=tool_parameters.get('table_names', None)  # Use get method with default value None
        )
        with_comment = tool_parameters.get('with_comment', False)
        dsl_text = format_schema_dsl(meta_data, with_type=True, with_comment=with_comment)
        print(dsl_text)
        # Initialize template loader
        prompt_loader = PromptLoader()
        # Build template context
        context = {
            'db_type': tool_parameters['db_type'].upper(),
            'meta_data': dsl_text
        }
        # Load dynamic prompt
        system_prompt = prompt_loader.get_prompt(
            db_type=tool_parameters['db_type'],
            context=context,
            limit=tool_parameters.get( 'limit', 100 ),
            user_custom_prompt=tool_parameters.get('custom_prompt', '')
        )
        print(f"System prompt:\n{system_prompt}")
        response = self.session.model.llm.invoke(
            model_config=LLMModelConfig(
                provider=model_info.get('provider'),
                model=model_info.get('model'),
                mode=model_info.get('mode'),
                completion_params=model_info.get('completion_params')
            ),
            prompt_messages=[
                SystemPromptMessage(content=system_prompt),
                UserPromptMessage(
                    content=f"Database type: {tool_parameters['db_type']}\n"
                            f"User requirement: {tool_parameters['query']}"
                )
            ],
            stream=False
        )
        print(response)
        excute_sql = response.message.content
        if (isinstance(excute_sql, str)):
            if (tool_parameters['result_format'] == 'json'):
                yield self.create_json_message({
                    "excute_sql": excute_sql
                })
            else:
                yield self.create_text_message(excute_sql)
        else:
            yield self.create_text_message("Generation failed, please check if the input parameters are correct")

    def _extract_sql_from_text(self, text: str) -> str:
        import re
        """Intelligently extract SQL content (compatible with cases with or without code block wrapping)"""
        # Match cases wrapped in code blocks
        code_block_pattern = r'(?s)```sql(.*?)```'
        code_match = re.search(code_block_pattern, text)
        if code_match:
            return code_match.group(1).strip()
        
        # Match pure SQL not wrapped
        sql_pattern = r'(?si)^\s*((?:SELECT|INSERT|UPDATE|DELETE|WITH|CREATE|ALTER|DROP).+?)(;|$|\n\s*$)'
        sql_match = re.search(sql_pattern, text, re.DOTALL)
        if sql_match:
            # Remove possible non-statement terminators at the end
            sql = sql_match.group(1).rstrip(';').strip()
            return f"{sql};" if sql_match.group(2) == ';' else sql
        
        # Fallback: return SQL-like parts from the original text
        clean_text = re.sub(r'[\n\r\t]+', ' ', text).strip()
        return clean_text if any(kw in clean_text.upper() for kw in ['SELECT', 'FROM', 'WHERE']) else ""
    
