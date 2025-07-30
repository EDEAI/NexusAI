from typing import Any
import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class BitlyShortnerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        access_token = credentials.get("access_token")
        if not access_token:
            raise ToolProviderCredentialValidationError("Bitly access token is required.")
        
        try:
            # Make a simple API call to validate the token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test with a simple API endpoint - get user info
            response = requests.get("https://api-ssl.bitly.com/v4/user", headers=headers)
            
            if response.status_code == 200:
                # Token is valid
                pass
            elif response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid Bitly access token. Please check your credentials.")
            elif response.status_code == 403:
                raise ToolProviderCredentialValidationError("Access denied. Please check your Bitly account permissions.")
            else:
                raise ToolProviderCredentialValidationError(f"Failed to validate Bitly credentials: HTTP {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Network error while validating credentials: {str(e)}")
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Error validating credentials: {str(e)}")
