from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GentelShieldTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = {
            "endpoint": self.runtime.credentials['endpoint'],
            "api_key": self.runtime.credentials['api_key'],
            "modal": tool_parameters["modal"],
            "role": "user",
            "text": tool_parameters["text"],
        }
        print(f'Request: {params}')
        result = self._call_func(params)
        print(f'Response: {result}')

        yield self.create_json_message(result)
        yield self.create_text_message(result.get('event_risk_level'))
        yield self.create_variable_message('defense_content', result.get('defense_content') if result.get('defense_content') is not None else "")
        yield self.create_variable_message('event_risk_level', result.get('event_risk_level', 'NO_RISK'))
        yield self.create_variable_message('risk_event', result.get('risk_event', []))

    def _call_func(self, input: dict[str, Any]) -> dict[str, Any]:
        url = f'{input["endpoint"]}/{input["modal"]}'
        headers = {
        'Shield-Api-Key': input['api_key'],
        }

        payload = {
            'text': input['text'],
            'role': input['role'],
        }

        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        body = response.json()
        if body.get('code') != 0:
            raise RuntimeError(body.get("message", "unknown error"))
        data = body.get('data')
        return data
