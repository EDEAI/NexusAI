from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.regex_extract import RegexExpressionTool
from dify_plugin import ToolProvider


class RegexProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            RegexExpressionTool().invoke(tool_parameters={"content": "1+(2+3)*4", "expression": "(\\d+)"})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
