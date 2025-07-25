from collections.abc import Generator
from typing import Any
import re
from markdown_it import MarkdownIt
from mdit_plain.renderer import RendererPlain

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RemoveMarkdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            text = tool_parameters.get("text", "")

            # Process markdown images before rendering
            text = re.sub(r'!\[([^]]+)]\(([^)]+)\)', r'\1( \2 )', text)
            # Process markdown links before rendering
            text = re.sub(r'\[([^]]+)]\(([^)]+)\)', r'\1[ \2 ]', text)

            parser = MarkdownIt(renderer_cls=RendererPlain)
            txt_data = parser.render(text)
            
            yield self.create_text_message(txt_data)
        except Exception as e:
            yield self.create_error_message(f"Error processing markdown: {str(e)}")

