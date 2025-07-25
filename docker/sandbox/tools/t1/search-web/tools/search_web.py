from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class LinkupSearchTool(Tool):
    def _parse_response(self, response: Any) -> dict:
        results = getattr(response, "results", [])
        parsed = []
        for doc in results:
            parsed.append({
                "title": doc.name or "Untitled",
                "url": doc.url or "N/A",
                "content": doc.content or "",
            })
        return {
            "search_results": parsed  
        }
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        from linkup import LinkupClient

        client = LinkupClient(api_key=self.runtime.credentials["linkup_api_key"])

        query = tool_parameters["query"]
        depth = tool_parameters["depth"]

        try:
            response = client.search(
                query=query,
                depth=depth,
                output_type="searchResults"
            )
        except Exception as e:
            raise RuntimeError(f"Linkup search failed: {str(e)}") from e

        valuable_res = self._parse_response(response)

        yield self.create_json_message(valuable_res)
