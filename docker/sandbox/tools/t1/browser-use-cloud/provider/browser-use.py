from typing import Any
import requests
import json

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class BrowserUseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Get the API key from credentials
            api_key = credentials.get('browser_use_api_key')
            if not api_key:
                print("[DEBUG] No API key provided in credentials")
                raise ValueError("Browser Use API key is required")
            
            print(f"[DEBUG] Validating Browser Use API key: {api_key[:4]}...{api_key[-4:]}")
            
            # Call the /me endpoint to validate the API key
            url = "https://api.browser-use.com/api/v1/me"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"[DEBUG] API validation failed with status code: {response.status_code}")
                error_message = f"API validation failed: {response.status_code} {response.reason}"
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'detail' in error_data:
                        error_message = f"API validation failed: {error_data['detail']}"
                    print(f"[DEBUG] Error response: {json.dumps(error_data, indent=2)}")
                except Exception:
                    print(f"[DEBUG] Could not parse error response as JSON: {response.text}")
                raise ValueError(error_message)
            
            # Check if the response is 'true'
            result = response.json()
            if result is not True:
                print(f"[DEBUG] API validation failed: Unexpected response: {result}")
                raise ValueError("API key validation failed: Invalid response from server")
            
            print("[DEBUG] Browser Use API key validation successful")
        except requests.RequestException as e:
            print(f"[DEBUG] Request error during API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(f"Could not connect to Browser Use API: {str(e)}")
        except ValueError as e:
            print(f"[DEBUG] Validation error: {str(e)}")
            raise ToolProviderCredentialValidationError(str(e))
        except Exception as e:
            print(f"[DEBUG] Unexpected error during API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(f"Unexpected error: {str(e)}")
