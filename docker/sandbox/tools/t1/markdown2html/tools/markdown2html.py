from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import markdown

class Markdown2htmlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        text = tool_parameters.get("text", "")
        md = markdown.Markdown()
        html = md.convert(text)
        yield self.create_text_message(html)
