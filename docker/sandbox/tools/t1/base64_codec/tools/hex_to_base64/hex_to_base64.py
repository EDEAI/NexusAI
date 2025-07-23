from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils.base64_utils import encode_bytes_to_base64


class HexToBase64Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        hex_text: str = tool_parameters.get("hex_text", "").strip()

        # remove possible "0x" prefix
        hex_text = hex_text.removeprefix("0x")

        if len(hex_text) % 2 != 0:
            raise ValueError(f"Invalid hex text, exception: the length of hex text must be an even number.")

        try:
            hex_bytes = bytes.fromhex(hex_text)
        except ValueError as e:
            raise ValueError(f"Invalid hex text, exception: {e}")

        urlsafe_enabled = bool("true" == tool_parameters.get("urlsafe_enabled", "").lower())
        try:
            result_base_str = encode_bytes_to_base64(hex_bytes, urlsafe_enabled)
        except Exception as e:
            raise ValueError("Failed to encode text input, Exception: " + str(e))

        yield self.create_text_message(result_base_str)
