from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep


class GetSessionMemoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            client = Zep(api_key=api_key)

            memory = client.memory.get(
                session_id=tool_parameters["session_id"],
                lastn=tool_parameters.get("lastn"),
                min_rating=tool_parameters.get("min_rating"),
            )

            yield self.create_json_message(
                {"status": "success", "memory": json.loads(memory.json())}
            )
            yield self.create_text_message(memory.context or "")
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
            yield self.create_text_message(f"failed to retrieve memory: {err}")
