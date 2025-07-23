from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class MicrosoftTodoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        access_token = credentials.get("access_token")

        if not access_token or not isinstance(access_token, str):
            raise ToolProviderCredentialValidationError("Missing or invalid Microsoft OAuth Access Token.")
