from collections.abc import Generator
import json
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

HELLODB_API_BASE = 'https://yun.sinapp.cn/api'

class HellodbTool(Tool):


    def _parse_response(self, response: dict) -> dict:
        result = {}
        print(response)
        if response and response['code'] == 200:
            if "data" in response:
                result["sql"] = response['data'].get("sql", "")
                result["data"] = response['data'].get("data", "")
                result["text"] = response['data'].get("text", "")
            return result
        else:
            raise Exception(response)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        app_key = tool_parameters['app_key']
        question = tool_parameters['query']

        api_key = self.runtime.credentials["api_key"]
        api_base = self.runtime.credentials["api_base"]

        api_base = HELLODB_API_BASE if not api_base or api_base == "" else api_base

        api_url = api_base + "/openapi/v0/datasource/chat"

        data = {
            "app_key": app_key,
            "question": question,
            "from": "dify plugin",
            "user_id": self.runtime.user_id,
            "plugin_version": "0.1.1"
        }

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url=api_url, headers=headers, data=json.dumps(data), timeout=30)
        response.raise_for_status()
        valuable_res = self._parse_response(response.json())
        
        yield self.create_json_message(valuable_res)


