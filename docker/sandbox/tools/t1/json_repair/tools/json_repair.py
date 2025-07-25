from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import json
import json_repair


class JsonRepairTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        text = tool_parameters.get("text", "")
        data = json_repair.loads(text)
        fixed_text = json.dumps(data, ensure_ascii=False)
        yield self.create_text_message(fixed_text)
