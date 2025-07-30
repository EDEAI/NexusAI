from typing import Any, Generator

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ToolInvokeError(Exception):
    pass


class StockHSTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        key = tool_parameters.get("apiKey", "")
        if not key:
            raise ToolProviderCredentialValidationError("Please provide the correct apiKey")

        gid = tool_parameters.get("gid", "")
        t = tool_parameters.get("type", -1)
        if not gid and t==-1:
            raise ToolInvokeError("Please provide gid/type parameter")

        url = "http://web.juhe.cn/finance/stock/hs"
        params = {
            "key": key,
            "gid": gid,
            "type": t,
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise ToolInvokeError(f"Request failed:{response.status_code} - {response.text}")
        yield self.create_text_message(response.text)

    def validate_credentials(self, parameters: dict[str, Any]) -> None:
        parameters["gid"] = ""
        parameters["type"] = 0
        for _ in self._invoke(parameters):
            break
