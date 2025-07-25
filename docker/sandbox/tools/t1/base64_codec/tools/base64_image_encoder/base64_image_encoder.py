import base64
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

from tools.utils.image_prefix_utils import wrap_mime_text_with_prefix


class Base64ImageEncoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        input_image: File = tool_parameters.get("input_image")
        if not input_image or not isinstance(input_image, File):
            raise ValueError("Not a valid file for input input_image")
        input_image_bytes = input_image.blob

        try:
            encoded_str = base64.b64encode(input_image_bytes).decode("utf-8")
            prefix = wrap_mime_text_with_prefix(input_image.mime_type)
            result_str = f"{prefix}{encoded_str}"
        except Exception as e:
            raise RuntimeError(f"Failed to encode image to Base64 encoded text, error: {str(e)}")

        yield self.create_text_message(result_str)
