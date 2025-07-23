from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GiteeAIToolText2Image(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        headers = {"content-type": "application/json", "authorization": f"Bearer {self.runtime.credentials['api_key']}"}
        payload = {
            "inputs": tool_parameters.get("inputs"),
            "width": tool_parameters.get("width", "720"),
            "height": tool_parameters.get("height", "720"),
        }
        model = tool_parameters.get("model", "Kolors")
        url = f"https://ai.gitee.com/api/serverless/{model}/text-to-image"
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            yield self.create_text_message(f"Got Error Response:{response.text}")
        yield self.create_blob_message(blob=response.content, meta={"mime_type": "image/jpeg"})
