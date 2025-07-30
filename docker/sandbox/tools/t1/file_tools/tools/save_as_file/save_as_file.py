from collections.abc import Generator
from typing import Any
import base64
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SaveAsFileTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        content = tool_parameters.get("content")
        filename = tool_parameters.get("filename")
        mime_type = tool_parameters.get("mime_type", "")
        format = tool_parameters.get("format", "raw")

        if not mime_type:
            mime_type, _ = mimetypes.guess_type(filename)
        if not mime_type:
            raise ValueError("MIME type could not be determined by filename. Please provide a valid MIME type explicitly.")

        file_blob = content.encode("utf-8") if format == "text" else base64.b64decode(content)

        yield self.create_blob_message(
            blob=file_blob,
            meta={
                "mime_type": mime_type,
                "filename": filename,
            },
        )
