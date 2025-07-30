from typing import Any, Generator

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ToolInvokeError(Exception):
    pass


class GooglenewsTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        key = self.runtime.credentials.get("x-rapidapi-key", "")
        host = self.runtime.credentials.get("x-rapidapi-host", "")
        if not all([key, host]):
            raise ToolProviderCredentialValidationError("Please input correct x-rapidapi-key and x-rapidapi-host")
        headers = {"x-rapidapi-key": key, "x-rapidapi-host": host}
        lr = tool_parameters.get("language_region", "")
        url = f"https://{host}/latest?lr={lr}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise ToolInvokeError(f"Error {response.status_code}: {response.text}")
        yield self.create_text_message(response.text)

    def validate_credentials(self, parameters: dict[str, Any]) -> None:
        parameters["validate"] = True
        self._invoke(parameters)
