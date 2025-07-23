from collections.abc import Generator
from typing import Any
import zipfile
import io

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ZipTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        files_input = tool_parameters.get("files")
        file_name = tool_parameters.get("file_name") or "files.zip"
        if not file_name.endswith(".zip"):
            file_name += ".zip"
        if files_input[0] is None:
            raise ValueError("No files provided")

        in_memory_zip = io.BytesIO()

        try:
            with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file in files_input:
                    zf.writestr(file.filename, file.blob)

            zip_bytes = in_memory_zip.getvalue()

            yield self.create_blob_message(zip_bytes, meta={"mime_type":"application/zip", "filename":file_name})
        finally:
            in_memory_zip.close()
