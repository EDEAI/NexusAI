import hashlib
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class HashCalculatorTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the hash calculation tool.
        """

        # Extract tool parameters
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Invalid input_text")
        algorithm = tool_parameters.get("algorithm", "")
        if not algorithm:
            yield self.create_text_message("Invalid algorithm")

        try:
            if algorithm == "md5":
                hash_obj = hashlib.md5()
            elif algorithm == "sha256":
                hash_obj = hashlib.sha256()
            elif algorithm == "sha1":
                hash_obj = hashlib.sha1()
            else:
                yield self.create_text_message("Unsupported algorithm")
                return

            hash_obj.update(input_text.encode())
            result = hash_obj.hexdigest()

            if result:
                yield self.create_text_message(str(result))
            else:
                yield self.create_text_message("Failed to calculate hash value")
        except Exception as e:
            yield self.create_text_message(f"Failed to perform operation, error: {str(e)}")