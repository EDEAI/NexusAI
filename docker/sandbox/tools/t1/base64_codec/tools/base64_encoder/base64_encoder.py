from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils.base64_utils import encode_to_base64


class Base64TextEncoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        plain_text: str = tool_parameters.get("plain_text")
        if not plain_text:
            yield self.create_text_message("")
            return

        urlsafe_enabled = bool("true" == tool_parameters.get("urlsafe_enabled", "").lower())
        try:
            encoded_str = encode_to_base64(plain_text, urlsafe_enabled)
        except Exception as e:
            raise ValueError("Failed to encode text input, Exception: " + str(e))

        yield self.create_text_message(encoded_str)
