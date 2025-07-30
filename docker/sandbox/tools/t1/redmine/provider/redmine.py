from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class RedmineProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            redmine_host = credentials.get("redmine_host")
            api_key = credentials.get("api_key")

            if not redmine_host:
                raise ToolProviderCredentialValidationError("Redmine host URL is required")

            if not api_key:
                raise ToolProviderCredentialValidationError("API key is required")

            # Remove trailing slash from host if present
            redmine_host = redmine_host.rstrip('/')

            # Test API connection with a simple request
            headers = {
                "X-Redmine-API-Key": api_key,
                "Content-Type": "application/json"
            }

            # Test with user info endpoint (lightweight request)
            response = requests.get(
                f"{redmine_host}/users/current.json",
                headers=headers,
                timeout=10
            )

            if response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API key")
            elif response.status_code == 404:
                raise ToolProviderCredentialValidationError("Invalid Redmine host URL or API not enabled")
            elif response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"Connection failed with status {response.status_code}")

        except requests.exceptions.ConnectionError:
            raise ToolProviderCredentialValidationError("Cannot connect to Redmine host")
        except requests.exceptions.Timeout:
            raise ToolProviderCredentialValidationError("Connection timeout to Redmine host")
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Request error: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
