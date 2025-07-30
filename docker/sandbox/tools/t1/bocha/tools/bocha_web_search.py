from collections.abc import Generator
from typing import Any

import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

BOCHA_API_URL = "https://api.bochaai.com/v1/web-search?utm_source=dify"

class BochaWebSearchTool(Tool):
    def _parse_response(self, response: dict) -> dict:
        result = {}
        if "data" in response:
            data = response["data"]
            if "webPages" in data:
                webPages = data["webPages"]
                if "value" in webPages:
                    result["webpage"] = [
                        {
                            "id": item.get("id", ""),
                            "name": item.get("name", ""),
                            "url": item.get("url", ""),
                            "snippet": item.get("snippet", ""),
                            "summary": item.get("summary", ""),
                            "siteName": item.get("siteName", ""),
                            "siteIcon": item.get("siteIcon", ""),
                            "datePublished": item.get("datePublished", "") or item.get("dateLastCrawled", ""),
                        }
                        for item in webPages["value"]
                    ]
            if "images" in data:
                images = data["images"]
                if "value" in images:
                    result["image"] = [
                        {
                            "id": item.get("id", ""),
                            "contentUrl": item.get("contentUrl", ""),
                            "hostPageUrl": item.get("hostPageUrl", ""),
                            "width": item.get("width", 0),
                            "height": item.get("height", 0),
                        }
                        for item in images["value"]
                    ]
        return result
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        freshness = "noLimit"
        if "freshness" in tool_parameters:
            freshness = tool_parameters["freshness"]

        count = 10
        if "count" in tool_parameters:
            count = tool_parameters["count"]

        payload = json.dumps({
            "query": tool_parameters["query"],
            "summary": True,
            "freshness": freshness,
            "count": count
        })

        headers = {
            "Authorization": f"Bearer {self.runtime.credentials["bocha_api_key"]}",
            "Content-Type": "application/json",
        }

        response = requests.post(url=BOCHA_API_URL, headers=headers, data=payload, timeout=5)

        response.raise_for_status()
        valuable_res = self._parse_response(response.json())
        
        yield self.create_json_message(valuable_res)
