from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class GoogleBooksExplorerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if not credentials.get("google_books_api_key"):
                raise ToolProviderCredentialValidationError(
                    "Missing required credential: 'google_books_api_key'"
                )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
