import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class AnspireBrowserAgentProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Get the API key from credentials
            api_key = credentials.get("api_key")
            if not api_key:
                raise ValueError("Browser Agent API key is required")

            print(
                f"[DEBUG] Validating Browser Agent API key: {api_key[:4]}...{api_key[-4:]}"
            )

            # validate the API key
            url = f"https://open.anspire.cn/v1/apiKey/me/{api_key}"

            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers={"Content-Type": "application/json"})

            # Check if the request was successful
            if response.status_code != 200:
                print(
                    f"[DEBUG] API validation failed with status code: {response.status_code}"
                )
                error_message = (
                    f"API validation failed: {response.status_code} {response.reason}"
                )
                try:
                    error_data = response.json()
                    print(f"[DEBUG] Error response: {error_data}")
                except Exception:
                    print(
                        f"[DEBUG] Could not parse error response as JSON: {response.text}"
                    )
                raise ValueError(error_message)

            # Check if the response is 'true'
            result = response.json()
            if not result:
                raise ValueError("API key validation error: not response from server")

            if not result.get("data", False):
                print(f"[DEBUG] API validation failed: Unexpected response: {result}")
                raise ValueError(
                    "API key validation failed: Invalid response from server"
                )

            print("[DEBUG] Browser Agent API key validation successful")
        except requests.RequestException as e:
            print(f"[DEBUG] Request error API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(
                f"Could not connect to Browser Agent API: {str(e)}"
            )
        except ValueError as e:
            print(f"[DEBUG] Validation error: {str(e)}")
            raise ToolProviderCredentialValidationError(str(e))
        except Exception as e:
            print(f"[DEBUG] Unexpected error API validation: {str(e)}")
            raise ToolProviderCredentialValidationError(f"Unexpected error: {str(e)}")
