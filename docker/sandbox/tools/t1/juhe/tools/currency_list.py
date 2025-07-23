from typing import Any, Generator

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ToolInvokeError(Exception):
    pass


class CurrencyListTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("apiKey", "")
        if not key:
            raise ToolProviderCredentialValidationError("Please provide the correct apiKey")

        url = "http://op.juhe.cn/onebox/exchange/list"
        params = {
            "key": key,
            "version": "2"
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ToolInvokeError(f"Request failed:{response.status_code} - {response.text}")
        yield self.create_text_message(response.text)

    def validate_credentials(self, parameters: dict[str, Any]) -> None:
        for _ in self._invoke(parameters):
            break
