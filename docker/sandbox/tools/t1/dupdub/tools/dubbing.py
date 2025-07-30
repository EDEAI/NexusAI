from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests
import json

def build_data(tool_parameters):
    try:
        text_list = tool_parameters.get("textList")
        if not text_list:
            raise ValueError("textList is empty or None")

        data = {
            "speaker": tool_parameters.get("speaker"),
            "speed": tool_parameters.get("speed"),
            "pitch": tool_parameters.get("pitch"),
            "textList": [tool_parameters.get("textList")]
        }
        return data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON format for textList")
    except ValueError as e:
        raise ValueError(f"Data validation error: {e}")
    
class DubbingTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dupdub_token = self.runtime.credentials.get("dupdub_token")
        """
        IMPLEMENT YOUR TOOL LOGIC HERE
        """
        url = "https://moyin-gateway.dupdub.com/tts/v1/playDemo/dubForSpeaker"
        headers = {
            "Content-Type": "application/json",
            "dupdub_token": dupdub_token,
        }
        data = build_data(tool_parameters)
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
