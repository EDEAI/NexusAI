from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.httpUtil import do_request


class AnspireSearchTool(Tool):

    def _parse_response(self, response: dict) -> dict:
        pass

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        _auth_key = self.runtime.credentials.get("api_key")
        _endpoint = self.runtime.credentials.get("endpoint")
        # 兼容老版本配置
        if not _endpoint.endswith("/search"):
            _endpoint = f"{_endpoint}/prosearch"
        else:
            _endpoint = str(_endpoint).replace("/search", "/prosearch")

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {_auth_key}",
        }
        _params = {
            "query": tool_parameters["query"],
            "mode": 0,
        }
        if tool_parameters.get("top_k"):
            _params["top_k"] = int(tool_parameters.get("top_k"))
        if tool_parameters.get("Insite"):
            _params["Insite"] = tool_parameters.get("Insite")
        if tool_parameters.get("FromTime"):
            _params["FromTime"] = tool_parameters.get("FromTime")
        if tool_parameters.get("ToTime"):
            _params["ToTime"] = tool_parameters.get("ToTime")

        _request_obj = (
            "GET",
            _endpoint,
            headers,
            _params,
            None,
        )

        _code, _data = do_request(_request_obj)

        if _code != 200:
            raise ValueError(_data)

        yield self.create_variable_message("anspire_search_result", _data)
