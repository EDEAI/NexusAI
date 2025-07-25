from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.executeCode import ExecuteCodeTool


class Judge0CEProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in ExecuteCodeTool.from_credentials(credentials).invoke(
                tool_parameters={"source_code": "print('hello world')", "language_id": 71}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
