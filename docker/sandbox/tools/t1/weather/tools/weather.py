'''
Author: baobaobao
Date: 2025-03-11 17:56:04
LastEditTime: 2025-03-12 17:49:01
LastEditors: baobaobao
'''
from collections.abc import Generator
from typing import List, Dict, Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
class WeatherTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        city = tool_parameters['city']
        get_city_code = self.get_city_code(city)
        city_code = get_city_code.get('location')[0].get('id')
        weather = self.weather(city_code)
        yield self.create_json_message(weather)

    def weather(self, city: str) -> dict[str, Any]:
       response = requests.get(f"https://devapi.qweather.com/v7/weather/now?location={city}&key={self.runtime.credentials['qweather_api_key']}")
       return response.json()
    def get_city_code(self, city: str) -> str:
        response = requests.get(f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={self.runtime.credentials['qweather_api_key']}")
        return response.json()

