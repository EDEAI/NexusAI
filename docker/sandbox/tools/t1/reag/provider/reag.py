from typing import Any

from dify_plugin import ToolProvider # type: ignore
from dify_plugin.errors.tool import ToolProviderCredentialValidationError # type: ignore


class ReagProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
