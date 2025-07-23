from typing import Any, Generator
from urllib.parse import urlencode
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool

BASE_URL = "https://api.serply.io/v1/scholar/"


class SerplyApi:
    """
    SerplyApi tool provider.
    """

    def __init__(self, api_key: str) -> None:
        """Initialize SerplyApi tool provider."""
        self.serply_api_key = api_key

    def run(self, query: str, **kwargs: Any) -> str:
        """Run query through SerplyApi and parse result."""
        params = {"q": query, "hl": kwargs.get("hl", "en"), "gl": kwargs.get("gl", "US"), "num": kwargs.get("num", 10)}
        location = kwargs.get("location", "US")
        headers = {
            "X-API-KEY": self.serply_api_key,
            "X-User-Agent": kwargs.get("device", "desktop"),
            "X-Proxy-Location": location,
            "User-Agent": "Dify",
        }
        url = f"{BASE_URL}{urlencode(params)}"
        res = requests.get(url, headers=headers)
        res = res.json()
        return self.parse_results(res)

    @staticmethod
    def parse_results(res: dict) -> str:
        """Process response from Serply News Search."""
        articles = res.get("articles", [])
        if not articles:
            raise ValueError(f"Got error from Serply: {res}")
        string = []
        for article in articles:
            try:
                if "doc" in article:
                    link = article["doc"]["link"]
                else:
                    link = article["link"]
                authors = [author["name"] for author in article["author"]["authors"]]
                string.append(
                    "\n".join(
                        [
                            f"Title: {article['title']}",
                            f"Link: {link}",
                            f"Description: {article['description']}",
                            f"Cite: {article['cite']}",
                            f"Authors: {', '.join(authors)}",
                            "---",
                        ]
                    )
                )
            except KeyError:
                continue
        content = "\n".join(string)
        return f"\nScholar results:\n {content}\n"


class ScholarSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the SerplyApi tool.
        """
        query = tool_parameters["query"]
        gl = tool_parameters.get("gl", "us")
        hl = tool_parameters.get("hl", "en")
        location = tool_parameters.get("location")
        api_key = self.runtime.credentials["serply_api_key"]
        result = SerplyApi(api_key).run(query, gl=gl, hl=hl, location=location)
        yield self.create_text_message(text=result)
