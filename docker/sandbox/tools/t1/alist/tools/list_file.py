from collections.abc import Generator
from typing import Any
from .api_utils import AListRequest

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.model import CredentialsValidateFailedError


class ListFileTool(Tool):
    def _invoke(
        self,
        tool_parameters: dict[str, Any],
    ) -> Generator[ToolInvokeMessage]:
        alist_base_url = self.runtime.credentials.get("alist_base_url")
        username = tool_parameters.get("username")
        password = tool_parameters.get("password")
        path = tool_parameters.get("path")
        page = tool_parameters.get("page", 1)
        page_size = tool_parameters.get("page_size", 500)
        if page_size > 500:
            raise CredentialsValidateFailedError("page_size must be less than 500")
        client = AListRequest(alist_base_url, username, password)

        res = client.list_file(path, page, page_size)
        yield self.create_json_message(res)
