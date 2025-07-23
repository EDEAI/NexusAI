from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests

class TranscribeSpeechTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dupdub_token = self.runtime.credentials.get("dupdub_token")
        """
        IMPLEMENT YOUR TOOL LOGIC HERE
        """
        url = "https://moyin-gateway.dupdub.com/moyin-tool/v1/asr/transcriptionsBatch"
        headers = {
            "Content-Type": "application/json",
            "dupdub_token": dupdub_token,
        }
        data = {
            "list": [
                {
                 "duration": tool_parameters.get("duration"),
                 "url": tool_parameters.get("url"),
                 "language": tool_parameters.get("language"),
                }
            ]
        }
        response = requests.post(url, headers=headers,json=data)
        if response.status_code == 200:
            response = response.json()
            bus_code = response.get("code")
            if bus_code == 200:
                response = response.get("data").get("list")[0]
            print(response)
        else:
            print("Failed to transcribe the speech. Status Code:", response.status_code)
            
        yield self.create_json_message(response)
