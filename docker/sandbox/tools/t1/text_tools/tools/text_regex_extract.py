import re
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RegexExtractTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the regex extraction tool.
        """

        # Extract tool parameters
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Invalid input_text")
        regex_pattern = tool_parameters.get("regex_pattern", "")
        if not regex_pattern:
            yield self.create_text_message("Invalid regex_pattern")
        regex_ignorecase = tool_parameters.get("regex_ignorecase", False)
        regex_multiline = tool_parameters.get("regex_multiline", False)
        regex_dotall = tool_parameters.get("regex_dotall", False)
        regex_ascii = tool_parameters.get("regex_ascii", False)

        try:
            # Set flags based on parameters
            flags = 0
            if regex_ignorecase:
                flags |= re.IGNORECASE
            if regex_multiline:
                flags |= re.MULTILINE
            if regex_dotall:
                flags |= re.DOTALL
            if regex_ascii:
                flags |= re.ASCII

            # Perform regex search
            matches = re.findall(regex_pattern, input_text, flags=flags)
            if matches:
                yield self.create_text_message(str(matches[0]))
                yield self.create_json_message({"all_matches": matches})
            else:
                yield self.create_text_message("No matches found.")
        except Exception as e:
            yield self.create_text_message(f"Failed to extract matches, error: {str(e)}")