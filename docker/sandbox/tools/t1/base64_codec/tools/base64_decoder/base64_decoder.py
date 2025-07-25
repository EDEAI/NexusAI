from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils.base64_utils import decode_base64_to_str


class Base64TextDecoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        encoded_text: str = tool_parameters.get("encoded_text")
        if not encoded_text:
            yield self.create_text_message("")
            return

        urlsafe_enabled = bool("true" == tool_parameters.get("urlsafe_enabled", "").lower())
        try:
            decoded_str = decode_base64_to_str(encoded_text, urlsafe_enabled)
        except Exception as e:
            raise ValueError("Failed to decode Base64 text input, Exception: " + str(e))

        yield self.create_text_message(decoded_str)
