import requests
from typing import Any, Generator
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class JinaSearchTool(Tool):
    _jina_search_endpoint = "https://s.jina.ai/"

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        query = tool_parameters["query"]
        headers = {"Accept": "application/json"}
        if "api_key" in self.runtime.credentials and self.runtime.credentials.get("api_key"):
            headers["Authorization"] = "Bearer " + self.runtime.credentials.get("api_key")
        if tool_parameters.get("image_caption", False):
            headers["X-With-Generated-Alt"] = "true"
        if tool_parameters.get("gather_all_links_at_the_end", False):
            headers["X-With-Links-Summary"] = "true"
        if tool_parameters.get("gather_all_images_at_the_end", False):
            headers["X-With-Images-Summary"] = "true"
        proxy_server = tool_parameters.get("proxy_server")
        if proxy_server is not None and proxy_server != "":
            headers["X-Proxy-Url"] = proxy_server
        if tool_parameters.get("no_cache", False):
            headers["X-No-Cache"] = "true"
        # max_retries = tool_parameters.get("max_retries", 3)
        response = requests.get(
            str(
                URL(self._jina_search_endpoint + query)),
                headers=headers,
                timeout=(10, 60),
                # max_retries=max_retries
        )
        yield self.create_text_message(response.text)
