from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from memobase import MemoBaseClient

class MemobaseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            MEMOBASE_URL = credentials.get("memobase_url","")
            MEMOBASE_API_KEY = credentials.get("memobase_api_key","")

            if not MEMOBASE_URL or not MEMOBASE_API_KEY:
                raise ToolProviderCredentialValidationError("Memobase URL and API key are required.")
            
            client = MemoBaseClient(
                project_url=MEMOBASE_URL,
                api_key=MEMOBASE_API_KEY,
            )
            
            client.get_config()

        except Exception as e:
            raise ToolProviderCredentialValidationError('Memobase credentials are invalid. Please check your Memobase URL and API key.') from e
