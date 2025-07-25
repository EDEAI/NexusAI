from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetDownloadUrlTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("file")
        format = tool_parameters.get("format", "plain")
        link_text = tool_parameters.get("link_text", "")

        link_text = link_text or file.filename
        result = f"[{link_text}]({file.url})" if format == "markdown" else file.url

        yield self.create_text_message(result)
