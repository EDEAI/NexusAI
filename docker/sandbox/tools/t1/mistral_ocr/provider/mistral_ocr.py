from typing import Any
import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider

try:
    from mistralai import Mistral
    MISTRAL_CLIENT_AVAILABLE = True
except ImportError:
    MISTRAL_CLIENT_AVAILABLE = False

MISTRAL_API_URL = "https://api.mistral.ai/v1/models"

class MistralOCRProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        api_key = credentials.get('mistral_api_key')

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(MISTRAL_API_URL, headers=headers)

            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"Mistral API key is invalid. Status code: {response.status_code}"
                )

        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to connect to Mistral API: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Error validating Mistral API credentials: {str(e)}")
        