from typing import Any
import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class TrelloProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate Trello API credentials by making a test API call.

        Args:
            credentials (dict[str, Any]): The Trello API credentials to validate.

        Raises:
            ToolProviderCredentialValidationError: If the credentials are invalid.
        """
        api_key = credentials.get("trello_api_key")
        token = credentials.get("trello_api_token")
        url = f"https://api.trello.com/1/members/me?key={api_key}&token={token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            if response.status_code == 401:
                raise ToolProviderCredentialValidationError(
                    "Invalid Trello credentials: Unauthorized."
                )
            raise ToolProviderCredentialValidationError(
                "Error validating Trello credentials"
            )
        except requests.exceptions.RequestException:
            raise ToolProviderCredentialValidationError(
                "Error validating Trello credentials"
            )
