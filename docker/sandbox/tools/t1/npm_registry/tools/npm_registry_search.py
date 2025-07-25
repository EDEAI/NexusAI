from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.client import NpmRegistryClient


class NpmSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query: str = tool_parameters.get("query", "")
        if not query:
            yield self.create_text_message("Please provide a search query.")
            return

        try:
            with NpmRegistryClient() as client:

                search_results = client.search_packages(query=query, size=10)
                yield self.create_json_message(search_results.model_dump())

        except Exception as e:
            raise Exception(f"An error occurred while searching npm packages: {str(e)}")
