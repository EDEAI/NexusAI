from typing import Any
import requests
from requests_oauthlib import OAuth1Session
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class XProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the X API credentials by attempting to verify credentials
        """
        try:
            # Check if all required credentials are provided
            required_credentials = ["api_key", "api_secret", "access_token", "access_token_secret"]
            for cred in required_credentials:
                if not credentials.get(cred):
                    raise ValueError(f"Missing required credential: {cred}")
            
            # Try to create an OAuth session
            oauth = OAuth1Session(
                credentials["api_key"],
                client_secret=credentials["api_secret"],
                resource_owner_key=credentials["access_token"],
                resource_owner_secret=credentials["access_token_secret"]
            )
            
            # Make a simple API call to verify credentials (get account info)
            response = oauth.get("https://api.twitter.com/2/users/me")
            
            if response.status_code != 200:
                raise ValueError(f"Invalid credentials. API response: {response.status_code} {response.text}")
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
