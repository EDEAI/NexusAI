from collections.abc import Generator
from typing import Any

from utils.core import conversation_storage_put_message

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class PutMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_brand = "cloudflare_d1_lite"
        db_metadata = {
            "account_id": tool_parameters["cloudflare_account_id"],
            "database_id": tool_parameters["cloudflare_d1_database_id"],
            "api_token": tool_parameters["cloudflare_api_token"],
        }
        role = tool_parameters["role"]
        text = tool_parameters["text"]

        put_msg = conversation_storage_put_message(
            db_brand=db_brand,
            db_metadata=db_metadata,
            conversation_id=tool_parameters["conversation_id"],
            role=role,
            text=text,
        )

        message_id = put_msg["message_id"]
        conversation_id = put_msg["conversation_id"]

        yield self.create_json_message(put_msg)
        yield self.create_variable_message("message_id", message_id)
        yield self.create_variable_message("conversation_id", conversation_id)
