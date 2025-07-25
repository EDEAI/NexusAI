from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.databaseUtil import delete_conversation
import json

class DelMessage(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_metadata = {
            "host": self.runtime.credentials["database_host"],
            "port": int(self.runtime.credentials["database_port"]),
            "username": self.runtime.credentials["database_username"],
            "password": self.runtime.credentials["database_password"]
        }
        delete_conversation(
            tool_parameters["conversation_id"],
            db_metadata
        )
        yield self.create_text_message("ok")
