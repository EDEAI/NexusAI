from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
import ast, json, requests

class SearchWithUrlQuery(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        searchPayload = {
            "q": tool_parameters["q"],
            "offset": tool_parameters.get("offset", 0),
            "limit": tool_parameters.get("limit", 20),
            "hitsPerPage": tool_parameters.get("hitsPerPage", 1),
            "page": tool_parameters.get("page", 1),
            "filter": tool_parameters.get("filter", None),
            "facets": ast.literal_eval(tool_parameters.get("facets")) if tool_parameters.get("facets", None) else None,
            "attributesToRetrieve": ast.literal_eval(tool_parameters.get("attributesToRetrieve")) if tool_parameters.get("attributesToRetrieve", None) else None,
            "attributesToCrop": ast.literal_eval(tool_parameters.get("attributesToCrop")) if tool_parameters.get("attributesToCrop", None) else None,
            "cropLength": tool_parameters.get("cropLength", 10),
            "cropMarker": tool_parameters.get("cropMarker", "…"),
            "attributesToHighlight": ast.literal_eval(tool_parameters.get("attributesToHighlight")) if tool_parameters.get("attributesToHighlight", None) else None,
            "highlightPreTag": tool_parameters.get("highlightPreTag", "<em>"),
            "highlightPostTag": tool_parameters.get("highlightPostTag", "</em>"),
            "showMatchesPosition": tool_parameters.get("showMatchesPosition", False),
            "sort": ast.literal_eval(tool_parameters.get("sort")) if tool_parameters.get("sort", None) else None,
            "matchingStrategy": tool_parameters.get("matchingStrategy", "last"),
            "showRankingScore": tool_parameters.get("showRankingScore", False),
            "showRankingScoreDetails": tool_parameters.get("showRankingScoreDetails", False),
            "rankingScoreThreshold": tool_parameters.get("rankingScoreThreshold", None),
            "attributesToSearchOn": ast.literal_eval(tool_parameters.get("attributesToSearchOn")) if tool_parameters.get("attributesToSearchOn", None) else None,
            "hybrid": json.loads(tool_parameters.get("hybrid")) if tool_parameters.get("hybrid", None) else None,
            "vector": ast.literal_eval(tool_parameters.get("vector")) if tool_parameters.get("vector", None) else None,
            "retrieveVectors": tool_parameters.get("retrieveVectors", False),
            "locales": ast.literal_eval(tool_parameters.get("locales")) if tool_parameters.get("locales", None) else None
        }

        response = requests.post(
            f"{self.runtime.credentials['base_url']}/indexes/{tool_parameters['indexUid']}/search",
            headers={"Authorization": f"Bearer {self.runtime.credentials['meilisearch_api_key']}"},
            json=searchPayload
        )
        yield self.create_json_message(response.json())
