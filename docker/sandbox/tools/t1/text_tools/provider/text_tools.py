from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.ds_thought_clean import DeepseekThoughtCleanTool
from dify_plugin import ToolProvider


class TextToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            DeepseekThoughtCleanTool().invoke(
                tool_parameters={"provider": "deepseek", "expression": "<details style=\"color:gray;background-color: #f8f8f8;padding: 8px;border-radius: 4px;\" open> <summary> Thinking... </summary>用户发来了“你好”。</details>你好！～"}
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
