from typing import Any, Generator

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ToolInvokeError(Exception):
    pass


class WeatherLifeTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("apiKey", "")
        if not key:
            raise ToolProviderCredentialValidationError("Please provide the correct apiKey")

        city = tool_parameters.get("city", "")
        if not city:
            raise ToolInvokeError("Please provide city parameter")

        url = "http://apis.juhe.cn/simpleWeather/life"
        params = {
            "key": key,
            "city": city
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ToolInvokeError(f"Request failed:{response.status_code} - {response.text}")
        yield self.create_text_message(response.text)

    def validate_credentials(self, parameters: dict[str, Any]) -> None:
        parameters["city"] = "上海"
        for _ in self._invoke(parameters):
            break
