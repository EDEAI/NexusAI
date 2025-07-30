from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.databaseUtil import get_conversation_messages
import json

class PutMessage(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_metadata = {
            "host": self.runtime.credentials["database_host"],
            "port": int(self.runtime.credentials["database_port"]),
            "username": self.runtime.credentials["database_username"],
            "password": self.runtime.credentials["database_password"]
        }
        messages = get_conversation_messages(
            tool_parameters["conversation_id"],
            tool_parameters["user_id"],
            db_metadata,
            tool_parameters.get("max_count")
        )
        yield self.create_text_message(json.dumps(messages, ensure_ascii=False))
        yield self.create_json_message(
            {"conversation": messages}
        )
