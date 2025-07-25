import base64
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils.image_prefix_utils import extract_mime_type


class Base64ImageDecoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        encoded_text: str = tool_parameters.get("encoded_text")
        output_filename: str = tool_parameters.get("output_filename")
        if not encoded_text:
            raise ValueError("Invalid input encoded_text")

        try:
            comma_index = encoded_text.index(",")
            prefix = encoded_text[:comma_index]
            encoded_text = encoded_text[comma_index:]
            image_mime_type = extract_mime_type(prefix)
        except ValueError:  # ValueError when comma is not found
            image_mime_type = "image/png"

        try:
            result_file_bytes = base64.decodebytes(encoded_text.encode())
        except Exception as e:
            raise RuntimeError(f"Failed to decode base64 image to {image_mime_type}, error: {str(e)}")

        yield self.create_blob_message(
            blob=result_file_bytes,
            meta={
                "mime_type": image_mime_type,
                "filename": output_filename,
            },
        )
