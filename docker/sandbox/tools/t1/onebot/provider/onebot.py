from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class OneBotProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        if not credentials.get("ob11_http_url"):
            raise ToolProviderCredentialValidationError("OneBot HTTP URL is required.")
