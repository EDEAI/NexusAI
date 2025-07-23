from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class OpenaiAudioProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_key = credentials.get("api_key")
            if not api_key:
                raise ValueError("API key is required")
                
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.openai.com/v1/models",
                headers=headers
            )
            
            if response.status_code != 200:
                error_message = f"API key validation failed with status code: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data and "message" in error_data["error"]:
                        error_message = f"API key validation failed: {error_data['error']['message']}"
                except:
                    pass
                raise ValueError(error_message)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
