from collections.abc import Generator
from typing import Any
from .api_utils import AListRequest

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class WriteFileTool(Tool):
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        alist_base_url = self.runtime.credentials.get("alist_base_url")
        username = tool_parameters.get("username")
        password = tool_parameters.get("password")
        path = tool_parameters.get("path")
        content = tool_parameters.get("content")
        client = AListRequest(alist_base_url, username, password)

        res = client.write_file(path, content)
        yield self.create_json_message(res)
