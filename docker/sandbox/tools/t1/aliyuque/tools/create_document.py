from typing import Any, Union
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base import AliYuqueTool
from dify_plugin import Tool
from collections.abc import Generator

class AliYuqueCreateDocumentTool(AliYuqueTool, Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        token = self.runtime.credentials.get("token", None)
        if not token:
            raise Exception("token is required")
        yield self.create_text_message(self.request("POST", token, tool_parameters, "/api/v2/repos/{book_id}/docs"))
