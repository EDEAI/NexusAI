from collections.abc import Generator
from typing import Any
from .api_utils import AListRequest

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RemoveFileTool(Tool):
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        alist_base_url = self.runtime.credentials.get("alist_base_url")
        username = tool_parameters.get("username")
        password = tool_parameters.get("password")
        path = tool_parameters.get("path")
        client = AListRequest(alist_base_url, username, password)

        res = client.remove_file(path)
        yield self.create_json_message(res)
