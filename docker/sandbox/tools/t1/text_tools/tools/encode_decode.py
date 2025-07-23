import base64
import urllib.parse
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class EncodeDecodeTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the encode/decode tool.
        """

        # Extract tool parameters
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Invalid input_text")
        operation = tool_parameters.get("operation", "")
        if not operation:
            yield self.create_text_message("Invalid operation")

        try:
            if operation == "url_encode":
                result = urllib.parse.quote(input_text)
            elif operation == "url_decode":
                result = urllib.parse.unquote(input_text)
            elif operation == "base64_encode":
                result = base64.b64encode(input_text.encode()).decode()
            elif operation == "base64_decode":
                result = base64.b64decode(input_text).decode()
            elif operation == "unicode_encode":
                result = input_text.encode('unicode_escape').decode()
            elif operation == "unicode_decode":
                result = str(bytes(input_text, 'utf-8').decode('unicode_escape'))
            else:
                result = ""

            if result:
                yield self.create_text_message(str(result))
            else:
                yield self.create_text_message("Unsupported operation")
        except Exception as e:
            yield self.create_text_message(f"Failed to perform operation, error: {str(e)}")