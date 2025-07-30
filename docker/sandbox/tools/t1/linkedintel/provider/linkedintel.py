from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class LinkedIntelProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get("api_key")

        if not api_key or not isinstance(api_key, str):
            raise ToolProviderCredentialValidationError("Missing or invalid Proxycurl API Key.")
