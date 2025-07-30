from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests
from utils.flomo_utils import send_flomo_note

class FlomoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        content = tool_parameters.get("content", "")
        api_url = self.runtime.credentials.get("api_url", "")
        try:
            send_flomo_note(api_url, content)
        except ValueError as e:
            yield self.create_text_message(str(e))
            return
        except requests.RequestException as e:
            yield self.create_text_message(f"Connection error: {str(e)}")
            return
        yield self.create_text_message(
            "Note created successfully! Your content has been sent to Flomo."
        )
        yield self.create_json_message({
            "status": "success",
            "content": content,
        })
