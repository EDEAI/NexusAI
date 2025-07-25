from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DataEyesSearchTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("dataeyes_api_key")
        base_url = (self.runtime.credentials.get("base_url") or "https://api.shuyanai.com").rstrip("/")
        search_endpoint = f"{base_url}/v1/search"

        if not api_key:
            yield self.create_text_message("DataEyes API key is missing. Please set the 'dataeyes_api_key' in credentials.")
            return

        q = tool_parameters.get("q", "")
        num = tool_parameters.get("num", 10)

        if not q:
            yield self.create_text_message("Please provide 'q' (query) parameter for search.")
            return

        if not isinstance(num, int):
            try:
                num = int(num)
            except Exception:
                num = 10

        params = {"q": q, "num": num}
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            response = requests.get(search_endpoint, headers=headers, params=params)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            yield self.create_text_message("Request failed. Please try again later.")
            return

        if result.get("code") == 0 and "data" in result:
            data = result["data"]
            yield self.create_json_message(data)

            original_query = data.get("originalQuery", "")
            web_pages = data.get("webPages", [])
            formatted_result = f"搜索关键词: {original_query}\n搜索结果数: {len(web_pages)}\n"
            for idx, page in enumerate(web_pages, 1):
                name = page.get("name", "")
                url = page.get("url", "")
                snippet = page.get("snippet", "")
                date_published = page.get("datePublished", "")
                formatted_result += f"\n[{idx}] {name}\n链接: {url}\n摘要: {snippet}\n发布时间: {date_published}\n"
            yield self.create_text_message(formatted_result)
        else:
            yield self.create_text_message(f"Error: {result.get('msg')}")
