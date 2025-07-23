from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import hashes
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class Md5SumTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        input_file: File = tool_parameters.get("input_file")
        if not input_file or not isinstance(input_file, File):
            raise ValueError("Not a valid file for input input_file")

        digest = hashes.Hash(hashes.MD5())
        digest.update(input_file.blob)
        hash_result = digest.finalize().hex()
        yield self.create_text_message(hash_result)
