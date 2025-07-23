from collections.abc import Generator
from typing import Any
import json

from utils.core import (
    conversation_storage_get_conv_xml_basic,
    conversation_storage_get_conv_json_basic
)

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetConversationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_brand = "cloudflare_d1_lite"
        db_metadata = {
            "account_id": tool_parameters["cloudflare_account_id"],
            "database_id": tool_parameters["cloudflare_d1_database_id"],
            "api_token": tool_parameters["cloudflare_api_token"],
        }
        conversation_id = tool_parameters["conversation_id"]
        max_round = tool_parameters.get("max_round", 50)
        user_input = tool_parameters.get("user_input")
        output_format = tool_parameters.get("format", "xml")
        
        if output_format == "xml":
            content = conversation_storage_get_conv_xml_basic(
                db_brand=db_brand,
                db_metadata=db_metadata,
                conversation_id=conversation_id,
                max_round=max_round,
            )
            content = f"<history>\n{content}\n</history>"
            
            if user_input:
                user_message_xml = f"""<latest><message>
    <role>user</role>
    <content>{user_input}</content>
</message></latest>"""
                content = f"{content}\n{user_message_xml}"
            yield self.create_text_message(content)
            
        elif output_format == "json":
            messages = conversation_storage_get_conv_json_basic(
                db_brand=db_brand,
                db_metadata=db_metadata,
                conversation_id=conversation_id,
                max_round=max_round,
            )
            
            if user_input:
                messages.append({"role": "user", "content": user_input})
            
            # 返回字符串格式的JSON
            yield self.create_text_message(json.dumps(messages, ensure_ascii=False))
            # 返回原生JSON格式
            yield self.create_json_message({"conversation": messages})
            
        else:
            raise ValueError(f"Unsupported format: {output_format}, only 'xml' and 'json' are supported")
