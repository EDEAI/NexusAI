from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SendMessageTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        agentapi_url = self.runtime.credentials.get('agentapi_url')
        content = tool_parameters.get('content')
        message_type = tool_parameters.get('type', 'user')

        if not content:
            yield self.create_text_message("Message content is required.")
            return

        try:
            response = requests.post(
                f"{agentapi_url}/message",
                json={"content": content, "type": message_type},
            )
            response.raise_for_status()
            yield self.create_json_message(response.json())
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error sending message: {e}")
