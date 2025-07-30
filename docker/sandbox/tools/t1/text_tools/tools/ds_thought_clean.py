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
        provider = tool_parameters.get("provider", "").strip()
        if not provider:
            yield self.create_text_message("Invalid provider")
        content = tool_parameters.get("content", "").strip()
        if not content:
            yield self.create_text_message("Invalid content")

        try:
            if provider == "think_xml_tags" or provider == "volcengine_0_0_12":
                answer = content.split("</think>")[-1].strip()
                reason = content.split("</think>")[0].split("<think>")[-1].strip()
            elif provider == "deepseek_0_0_5":
                answer = content.split("</details>")[-1].strip()
                reason = content.split("</details>")[0].split("</summary>")[-1].strip()
            else:
                answer = content
                reason = ""
            yield self.create_text_message(str(answer))
            yield self.create_variable_message(variable_name="answer", variable_value=str(answer))
            yield self.create_variable_message(variable_name="reason", variable_value=str(reason))
        except Exception as e:
            yield self.create_text_message(f"Failed to extract result, error: {str(e)}")
