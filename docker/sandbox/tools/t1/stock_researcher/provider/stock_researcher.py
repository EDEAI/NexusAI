from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class StockResearcherProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            if not credentials.get("financial_api_key"):
                print("Missing required credential: financial_api_key")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
