import re
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DeepseekThoughtCleanTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """

        # extract tool_parameters
        input_text = tool_parameters.get("input_text", "")
        if not input_text:
            yield self.create_text_message("Invalid input_text")
        search_text = tool_parameters.get("search_text", "")
        if not search_text:
            yield self.create_text_message("Invalid search_text")
        replace_text = tool_parameters.get("replace_text", "")
        use_regex = tool_parameters.get("use_regex", False)
        regex_ignorecase = tool_parameters.get("regex_ignorecase", False)
        regex_multiline = tool_parameters.get("regex_multiline", False)
        regex_dotall = tool_parameters.get("regex_dotall", False)
        regex_ascii = tool_parameters.get("regex_ascii", False)

        try:
            if use_regex:
                flags = 0
                if regex_ignorecase:
                    flags |= re.IGNORECASE
                if regex_multiline:
                    flags |= re.MULTILINE
                if regex_dotall:
                    flags |= re.DOTALL
                if regex_ascii:
                    flags |= re.ASCII
                result = re.sub(pattern=search_text, repl=replace_text, string=input_text, flags=flags)
            else:
                result = input_text.replace(search_text, replace_text)
            yield self.create_text_message(str(result))
        except Exception as e:
            yield self.create_text_message(f"Failed to extract result, error: {str(e)}")
