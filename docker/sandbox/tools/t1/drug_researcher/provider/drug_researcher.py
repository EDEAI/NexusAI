from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DrugResearcherProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if not credentials.get("drugbank_api_key"):
                print("Missing required credential: 'drugbank_api_key'")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
