import json
from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class PoiSearchTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        geocoder_base_url = "http://api.tianditu.gov.cn/geocoder"
        base_url = "http://api.tianditu.gov.cn/v2/search"
        keyword = tool_parameters.get("keyword", "")
        if not keyword:
            yield self.create_text_message("Invalid parameter keyword")
            return
        baseAddress = tool_parameters.get("baseAddress", "")
        if not baseAddress:
            yield self.create_text_message("Invalid parameter baseAddress")
            return
        tk = self.runtime.credentials["tianditu_api_key"]
        base_coords = requests.get(
            geocoder_base_url
            + "?ds="
            + json.dumps({"keyWord": baseAddress}, ensure_ascii=False)
            + "&tk="
            + tk
        ).json()
        params = {
            "keyWord": keyword,
            "queryRadius": 5000,
            "queryType": 3,
            "pointLonlat": str(base_coords["location"]["lon"])
            + ","
            + str(base_coords["location"]["lat"]),
            "start": 0,
            "count": 100,
        }
        result = requests.get(
            base_url
            + "?postStr="
            + json.dumps(params, ensure_ascii=False)
            + "&type=query&tk="
            + tk
        ).json()
        yield self.create_json_message(result)
