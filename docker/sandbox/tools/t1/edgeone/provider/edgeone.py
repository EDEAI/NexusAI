import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class EdgeoneProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            api_token = credentials.get("api_token")
            
            # API token is optional - HTML deployment works without it
            # Only validate if token is provided
            if not api_token:
                return
            
            # Test API endpoints to validate token
            base_urls = [
                'https://pages-api.cloud.tencent.com/v1',
                'https://pages-api.edgeone.ai/v1'
            ]
            
            headers = {
                'Authorization': f'Bearer {api_token}',
                'Content-Type': 'application/json',
            }
            
            body = {
                'Action': 'DescribePagesProjects',
                'PageNumber': 1,
                'PageSize': 10,
            }
            
            # Try both API endpoints
            for base_url in base_urls:
                try:
                    response = requests.post(
                        base_url,
                        headers=headers,
                        json=body,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get('Code') == 0:
                            # API token is valid
                            return
                except requests.RequestException:
                    continue
            
            # If we get here, the token is invalid
            raise ToolProviderCredentialValidationError(
                "Invalid EdgeOne Pages API token. Please check your API token and try again. "
                "For more information, visit https://edgeone.ai/document/177158578324279296"
            )
            
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Credential validation failed: {str(e)}")
