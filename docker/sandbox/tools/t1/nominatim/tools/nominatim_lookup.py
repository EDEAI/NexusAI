import json
from typing import Any, Generator

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class NominatimLookupTool(Tool):
    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        osm_ids = tool_parameters.get("osm_ids", "")
        if not osm_ids:
            yield self.create_text_message("Please provide OSM IDs")
        params = {"osm_ids": osm_ids, "format": "json", "addressdetails": 1}
        yield self._make_request("lookup", params)

    def _make_request(self, endpoint: str, params: dict) -> ToolInvokeMessage:
        base_url = self.runtime.credentials.get("base_url", "https://nominatim.openstreetmap.org")
        try:
            headers = {"User-Agent": "DifyNominatimTool/1.0"}
            s = requests.session()
            response = s.request(method="GET", headers=headers, url=f"{base_url}/{endpoint}", params=params)
            response_data = response.json()
            if response.status_code == 200:
                s.close()
                return self.create_text_message(
                    self.session.model.summary.invoke(text=json.dumps(response_data, ensure_ascii=False),
                                                      instruction="")
                )
            else:
                return self.create_text_message(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            return self.create_text_message(f"An error occurred: {str(e)}")
