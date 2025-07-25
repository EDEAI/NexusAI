from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class TianyanchaDifyPluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Get token
            token = credentials.get("token")
            print(f"token: {token}")
            if not token:
                raise ToolProviderCredentialValidationError("API token cannot be empty")
                
            # Make a simple API call to validate the token
            url = "http://open.api.tianyancha.com/services/open/ic/baseinfo/normal?keyword=北京百度网讯科技有限公司"
            headers = {'Authorization': token}
            
            response = requests.get(url, headers=headers)
            
            # Validate response
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"API validation failed, status code: {response.status_code}")
                
            # Check API response result
            response_data = response.json()
            if response_data.get("error_code") != 0:
                error_msg = response_data.get("reason", "Unknown error")
                raise ToolProviderCredentialValidationError(f"API validation failed: {error_msg}")
                
        except ToolProviderCredentialValidationError:
            # Re-raise custom validation errors directly
            raise
        except Exception as e:
            # Handle other possible errors
            raise ToolProviderCredentialValidationError(f"Credential validation failed: {str(e)}")
