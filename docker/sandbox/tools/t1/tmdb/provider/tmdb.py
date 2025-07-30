from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class TmdbProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if 'api_key' not in credentials or not credentials.get('api_key'):
                raise ValueError("TMDB API Key is required")
            
            # Test API key with a simple request to authentication API using Bearer token
            api_key = credentials.get('api_key')
            headers = {
                'Authorization': f'Bearer {api_key}',
                'accept': 'application/json'
            }
            
            response = requests.get(
                "https://api.themoviedb.org/3/authentication",
                headers=headers
            )
            
            if response.status_code != 200:
                raise ValueError(f"Invalid API key or API request failed: {response.status_code}")
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
