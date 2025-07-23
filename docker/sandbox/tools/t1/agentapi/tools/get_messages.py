from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetMessagesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        agentapi_url = self.runtime.credentials.get('agentapi_url')
        try:
            response = requests.get(f"{agentapi_url}/messages")
            response.raise_for_status()
            yield self.create_json_message(response.json())
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error getting messages: {e}")
