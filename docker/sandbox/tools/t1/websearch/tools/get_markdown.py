from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

BASE_URL = "https://api.serply.io/v1/request"


class SerplyApi:
    """
    SerplyAPI tool provider.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize SerplyAPI tool provider."""
        self.serply_api_key = api_key

    def run(self, url: str, **kwargs: Any) -> str:
        """Run query through SerplyAPI and parse result."""
        location = kwargs.get("location", "US")
        headers = {
            "X-API-KEY": self.serply_api_key,
            "X-User-Agent": kwargs.get("device", "desktop"),
            "X-Proxy-Location": location,
            "User-Agent": "Dify",
        }
        data = {"url": url, "method": "GET", "response_type": "markdown"}
        res = requests.post(url, headers=headers, json=data)
        return res.text


class GetMarkdownTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the SerplyApi tool.
        """
        url = tool_parameters["url"]
        location = tool_parameters.get("location")
        api_key = self.runtime.credentials["serply_api_key"]
        result = SerplyApi(api_key).run(url, location=location)
        yield self.create_text_message(text=result)
