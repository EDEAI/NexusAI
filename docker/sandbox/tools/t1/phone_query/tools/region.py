from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils import PhoneNumberUtils

class DifyPluginPhoneTool(Tool):
   def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        number = tool_parameters.get("number", '')
        yield self.create_json_message(PhoneNumberUtils.get_location_info(number))