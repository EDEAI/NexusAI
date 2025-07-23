from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DupdubProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            if not credentials.get("dupdub_token"):
                raise ToolProviderCredentialValidationError("DupDub token is required")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
