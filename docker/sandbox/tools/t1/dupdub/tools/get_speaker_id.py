from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests

class GetSpeakerIdTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dupdub_token = self.runtime.credentials.get("dupdub_token")
        """
        IMPLEMENT YOUR TOOL LOGIC HERE
        """
        url = "https://moyin-gateway.dupdub.com/tts/v1/storeSpeakerV2/searchSpeakerList"
        headers = {
            "Content-Type": "application/json",
            "dupdub_token": dupdub_token,
        }

        # 使用 params 参数来拼接查询参数
        params = {
            "pageNum": 1,
            "pageSize": 2000
        }
        
        response = requests.get(url, headers=headers,params=params)
        if response.status_code == 200:
            response = response.json()
            bus_code = response.get("code")
            if bus_code == 200:
                data = response.get("data", {}).get("results", [])
                new_array = [{"speakerId": item["speakerId"], "speaker": item["speaker"], "name": item["name"]} for item in data]
                response = {"speakers": new_array}
            print(response)
        else:
            print("Failed to GetSpeakerId. Status Code:", response.status_code)
            
        yield self.create_json_message(response)
