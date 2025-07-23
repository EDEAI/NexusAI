from collections.abc import Generator
from typing import Any
import base64
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DumpToJsonTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("file")
        include_blob = tool_parameters.get("include_blob", 'false') == "true"

        file_dict = file.dict()
        if include_blob:
            file_dict["blob"] = base64.b64encode(file.blob).decode("utf-8")
        else:
            file_dict.pop("blob", None)

        yield self.create_text_message(
            json.dumps(file_dict, indent=2, ensure_ascii=False)
        )
