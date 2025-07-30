from collections.abc import Generator
from typing import Any

from ytelegraph import TelegraphAPI

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TelegraphTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        access_token = self.runtime.credentials["telegraph_access_token"]
        ph = TelegraphAPI(access_token)
        title = tool_parameters["p_title"]
        content = tool_parameters["p_content"]
        ph_link = ph.create_page_md(title, content)
        yield self.create_link_message(ph_link)
