from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests
from utils.flomo_utils import send_flomo_note

class FlomoProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_url = credentials.get('api_url', '').strip()
            # Use utility for validation and sending test note
            send_flomo_note(api_url, "Hello, #flomo https://flomoapp.com")
        except ValueError as e:
            raise ToolProviderCredentialValidationError(str(e))
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Connection error: {str(e)}")
