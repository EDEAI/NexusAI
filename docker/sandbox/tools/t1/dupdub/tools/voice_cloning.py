from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests

class VoiceCloningTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dupdub_token = self.runtime.credentials.get("dupdub_token")
        """
        IMPLEMENT YOUR TOOL LOGIC HERE
        """
        url = "https://moyin-gateway.dupdub.com/tts/v1/speakerClone"
        headers = {
            "Content-Type": "application/json",
            "dupdub_token": dupdub_token,
        }
        data = {
            "name": tool_parameters.get("name"),
            "url": tool_parameters.get("url"),
            "language": tool_parameters.get("language"),
            "accent": "",
            "gender": tool_parameters.get("gender"),
            "age": tool_parameters.get("age"),
            "style": tool_parameters.get("style")
        }   
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response = response.json()
            bus_code = response.get("code")
            if bus_code == 200:
                response = response.get("data")
            print(response)
        else:
            print("Failed to transcribe the speech. Status Code:", response.status_code)
            
        yield self.create_json_message(response)
