from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests

class ParseVideoSourceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dupdub_token = self.runtime.credentials.get("dupdub_token")
        """
        IMPLEMENT YOUR TOOL LOGIC HERE
        """
        url = "https://moyin-gateway.dupdub.com/moyin-tool/v1/videoToAudio/achieveVideoInfoV2"
        headers = {
            "Content-Type": "application/json",
            "dupdub_token": dupdub_token,
        }
        data = {
            "videoUrl": tool_parameters.get("video_url")
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response = response.json()
            response = response.get("data")
            print(response)
        else:
            print("Failed to transcribe the speech. Status Code:", response.status_code)
            
        yield self.create_json_message(response)
