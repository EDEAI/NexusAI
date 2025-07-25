from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class ImagetoolProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            tonyi_api_key = credentials.get('tonyi_api_key')
            if not tonyi_api_key:
                raise ValueError("Tonyi API key is required")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
