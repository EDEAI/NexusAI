from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class TripmgProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")
        api_secret = credentials.get("api_secret")

        if not api_key or not isinstance(api_key, str):
            raise ToolProviderCredentialValidationError("Missing or invalid Amadeus API Key.")
        if not api_secret or not isinstance(api_secret, str):
            raise ToolProviderCredentialValidationError("Missing or invalid Amadeus API Secret.")
