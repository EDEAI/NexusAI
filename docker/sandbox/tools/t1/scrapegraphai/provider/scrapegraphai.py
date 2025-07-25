from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ScrapegraphaiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Verify that the provided ScrapegraphAI API key is valid.
        Makes a request to the validation endpoint to check the API key.
        If validation fails, a ToolProviderCredentialValidationError exception is thrown.
        """
        api_key = credentials.get('scrapegraphai_api_key')
        if not api_key:
            raise ToolProviderCredentialValidationError("ScrapegraphAI API key cannot be empty.")

        try:
            # Make a request to the validation endpoint
            headers = {
                'SGAI-APIKEY': api_key
            }
            
            response = requests.get(
                'https://api.scrapegraphai.com/v1/validate',
                headers=headers
            )
            
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(
                    f"Invalid ScrapegraphAI API key. Server returned status code: {response.status_code}"
                )
                
        except requests.RequestException as e:
            raise ToolProviderCredentialValidationError(
                f"Failed to validate ScrapegraphAI credentials: {str(e)}"
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Unexpected error during ScrapegraphAI credential validation: {str(e)}"
            )
