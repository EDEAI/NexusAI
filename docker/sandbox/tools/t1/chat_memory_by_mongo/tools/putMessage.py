from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.databaseUtil import create_message, create_conversation

class PutMessage(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_metadata = {
            "host": self.runtime.credentials["database_host"],
            "port": int(self.runtime.credentials["database_port"]),
            "username": self.runtime.credentials["database_username"],
            "password": self.runtime.credentials["database_password"]
        }
        create_conversation(tool_parameters["conversation_id"], tool_parameters["user_id"], db_metadata)
        messageId = create_message(
            tool_parameters["conversation_id"],
            tool_parameters["user_id"],
            tool_parameters["role"],
            tool_parameters["text"],
            db_metadata
        )
        yield self.create_json_message({
            "message_id": messageId
        })
