from typing import Any
import requests
import logging

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnsplashProvider(ToolProvider):
    """Unsplash API Tool Provider
    Interface for Unsplash image search functionality
    """
    
    API_BASE_URL = "https://api.unsplash.com"
    
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """Validate Unsplash API credentials
        
        Args:
            credentials: Credential dictionary containing access_key
            
        Raises:
            ToolProviderCredentialValidationError: When credential validation fails
        """
        try:
            access_key = credentials.get('access_key')
            if not access_key:
                raise ValueError("Unsplash Access Key cannot be empty")
            
            # Test API key with a simple request
            headers = {
                'Authorization': f'Client-ID {access_key}'
            }
            
            # Test if the API key is valid
            test_url = f"{self.API_BASE_URL}/photos"
            logger.info(f"Testing Unsplash API with a request to {test_url}")
            
            response = requests.get(test_url, headers=headers)
            
            if response.status_code == 401:
                raise ValueError("Invalid Unsplash Access Key")
            elif response.status_code == 403:
                raise ValueError("Unsplash API permission denied, please check your application status")
            elif response.status_code == 429:
                raise ValueError("Exceeded Unsplash API request limit, please try again later")
            elif response.status_code != 200:
                raise ValueError(f"API request failed, status code: {response.status_code}, error: {response.text}")
                
            logger.info("Unsplash API credentials validation successful")
            
        except requests.RequestException as e:
            error_msg = f"API request exception: {str(e)}"
            logger.error(error_msg)
            raise ToolProviderCredentialValidationError(error_msg)
        except Exception as e:
            error_msg = f"Credential validation failed: {str(e)}"
            logger.error(error_msg)
            raise ToolProviderCredentialValidationError(error_msg)
