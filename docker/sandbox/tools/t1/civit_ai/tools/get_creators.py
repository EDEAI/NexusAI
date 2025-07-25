from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .civitai_client import CivitAI


class GetCreators(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("civitai_api_key")
        if not api_key:
            yield self.create_text_message("Please input api_key")
        cli = CivitAI(api_key)
        json = cli.get_creators(limit=tool_parameters.get("limit", 20),
                                page=tool_parameters.get("page"),
                                query=tool_parameters.get("query"))
        yield self.create_json_message(json)

        mapping = {"username": [item["username"]
                                for item in json["items"]],
                   "link": [item["link"]
                            for item in json["items"]]}
        for key in mapping:
            yield self.create_variable_message(
                key, mapping[key]
            )
