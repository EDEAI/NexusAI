from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.shield import GentelShieldTool


class GentelProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in GentelShieldTool.from_credentials(credentials).invoke(
                tool_parameters={"modal": "text", "text": "test"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
