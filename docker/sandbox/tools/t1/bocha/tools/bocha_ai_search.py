from collections.abc import Generator
from typing import Any

import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

BOCHA_API_URL = "https://api.bochaai.com/v1/ai-search?utm_source=dify"

class BochaAISearchTool(Tool):
    def _parse_response(self, response: dict) -> dict:
        result = {}
        if "messages" in response:
            for message in response["messages"]:
                content = {}
                try:
                    content = json.loads(message["content"])
                except:
                    content = {}

                # 网页
                if message["content_type"] == "webpage":
                    if "value" in content:
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
                        for item in content["value"]
                    ]
                # 图片
                elif message["content_type"] == "image":
                    if "value" in content:
                        result["image"] = [
                        {
                            "id": item.get("id", ""),
                            "contentUrl": item.get("contentUrl", ""),
                            "hostPageUrl": item.get("hostPageUrl", ""),
                            "width": item.get("width", 0),
                            "height": item.get("height", 0),
                        }
                        for item in content["value"]
                    ]
                else:
                    result[message["content_type"]] = content
        return result
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        freshness = "noLimit"
        if "freshness" in tool_parameters:
            freshness = tool_parameters["freshness"]

        payload = json.dumps({
            "query": tool_parameters["query"],
            "freshness": freshness,
            "answer": False,
            "stream": False
        })

        headers = {
            "Authorization": f"Bearer {self.runtime.credentials["bocha_api_key"]}",
            "Content-Type": "application/json",
        }

        response = requests.post(url=BOCHA_API_URL, headers=headers, data=payload, timeout=5)

        response.raise_for_status()
        valuable_res = self._parse_response(response.json())
        
        yield self.create_json_message(valuable_res)
