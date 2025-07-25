from collections.abc import Generator
from typing import Any, Optional
import requests
import logging
import time
from urllib.parse import urljoin
import io

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UnsplashRandomTool(Tool):
    """Unsplash Random Photo Tool
    Provides functionality to get random photos from Unsplash
    """
    
    API_BASE_URL = "https://api.unsplash.com"
    
    def get_credentials(self) -> dict[str, Any]:
        """Get Unsplash API credentials"""
        return self.runtime.credentials
    
    def _validate_parameters(self, tool_parameters: dict[str, Any]) -> None:
        """Validate input parameters
        
        Args:
            tool_parameters: Tool parameters
            
        Raises:
            ValueError: When parameters are invalid
        """
        # Validate count parameter
        count = tool_parameters.get('count', 1)
        if not isinstance(count, (int, float)) or count <= 0 or count > 30:
            raise ValueError("Photo count must be an integer between 1 and 30")
    
    def _build_photo_object(self, photo: dict) -> dict:
        """Build photo object from API response
        
        Args:
            photo: Raw photo data
            
        Returns:
            Structured photo object
        """
        return {
            'id': photo.get('id'),
            'description': photo.get('description'),
            'alt_description': photo.get('alt_description'),
            'width': photo.get('width'),
            'height': photo.get('height'),
            'color': photo.get('color'),
            'likes': photo.get('likes'),
            'created_at': photo.get('created_at'),
            'updated_at': photo.get('updated_at'),
            'urls': {
                'raw': photo.get('urls', {}).get('raw'),
                'full': photo.get('urls', {}).get('full'),
                'regular': photo.get('urls', {}).get('regular'),
                'small': photo.get('urls', {}).get('small'),
                'thumb': photo.get('urls', {}).get('thumb'),
            },
            'user': {
                'id': photo.get('user', {}).get('id'),
                'name': photo.get('user', {}).get('name'),
                'username': photo.get('user', {}).get('username'),
                'portfolio_url': photo.get('user', {}).get('portfolio_url'),
                'profile_image': photo.get('user', {}).get('profile_image'),
            },
            'links': {
                'self': photo.get('links', {}).get('self'),
                'html': photo.get('links', {}).get('html'),
                'download': photo.get('links', {}).get('download'),
                'download_location': photo.get('links', {}).get('download_location'),
            }
        }
        
    def _download_image(self, url: str) -> bytes:
        """Download image and return binary data
        
        Args:
            url: Image URL
            
        Returns:
            Image binary data
        """
        try:
            logger.info(f"Downloading image: {url}")
            response = requests.get(url, stream=True)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.error(f"Failed to download image: {str(e)}")
            raise
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Execute Unsplash random photo retrieval
        
        Args:
            tool_parameters: Tool parameters
            
        Yields:
            ToolInvokeMessage: Tool invocation messages
        """
        try:
            # Validate parameters
            self._validate_parameters(tool_parameters)
            
            # Get parameters
            query = tool_parameters.get('query')
            count = min(int(tool_parameters.get('count', 1)), 30)
            orientation = tool_parameters.get('orientation')
            color = tool_parameters.get('color')
            
            # Get credentials
            credentials = self.get_credentials()
            access_key = credentials.get('access_key')
            
            # Set API request headers
            headers = {
                'Authorization': f'Client-ID {access_key}'
            }
            
            # Build API request URL and parameters
            url = urljoin(self.API_BASE_URL, '/photos/random')
            params = {
                'count': count
            }
            
            # Add optional parameters
            if query:
                params['query'] = query
            if orientation:
                params['orientation'] = orientation
            if color:
                params['color'] = color
            
            logger.info(f"Fetching random photos from Unsplash with parameters: {params}")
            
            # Send API request
            start_time = time.time()
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            # Process response data
            # Random photo API returns an object for a single photo, an array for multiple photos
            photos_data = response.json()
            if not isinstance(photos_data, list):
                photos_data = [photos_data]
                
            request_time = time.time() - start_time
            logger.info(f"Unsplash API request completed in {request_time:.2f} seconds")
            
            # Create text message with retrieval results summary
            param_desc = []
            if query:
                param_desc.append(f"query='{query}'")
            if orientation:
                param_desc.append(f"orientation='{orientation}'")
            if color:
                param_desc.append(f"color='{color}'")
                
            param_str = ", ".join(param_desc) if param_desc else "no filters applied"
            summary_text = f"Retrieved {len(photos_data)} random photos ({param_str})"
            yield self.create_text_message(summary_text)
            
            # Handle case with no results
            if not photos_data:
                yield self.create_json_message({
                    'photos': [],
                    'error': None,
                    'parameters': {
                        'query': query,
                        'count': count,
                        'orientation': orientation,
                        'color': color
                    }
                })
                yield self.create_variable_message('random_photos', [])
                return
            
            # Build return results
            photos = []
            photo_details = []
            
            for photo in photos_data:
                # Build photo object
                photo_data = self._build_photo_object(photo)
                photos.append(photo_data)
                
                # Get image URL
                image_url = photo.get('urls', {}).get('regular')
                if image_url:
                    try:
                        # Download image
                        image_data = self._download_image(image_url)
                        
                        # Add image description
                        description = (
                            photo.get('description') or 
                            photo.get('alt_description') or 
                            f"Photo by {photo.get('user', {}).get('name', 'Unknown')}"
                        )
                        
                        # Create filename
                        photo_id = photo.get('id', 'photo')
                        filename = f"unsplash_random_{photo_id}.jpg"
                        
                        # Use blob_message to send image data
                        yield self.create_blob_message(
                            blob=image_data,
                            meta={
                                "mime_type": "image/jpeg",
                                "filename": filename,
                                "description": description
                            }
                        )
                        
                        # Add photo details to list, rather than outputting as text messages
                        user_name = photo.get('user', {}).get('name', 'Unknown')
                        user_link = photo.get('user', {}).get('links', {}).get('html', '')
                        photo_link = photo.get('links', {}).get('html', '')
                        dimensions = f"{photo.get('width', 'Unknown')}x{photo.get('height', 'Unknown')}"
                        
                        photo_detail = {
                            'id': photo.get('id'),
                            'description': description,
                            'dimensions': dimensions,
                            'author': user_name,
                            'photo_link': photo_link,
                            'user_link': user_link,
                            'license': "Unsplash License - https://unsplash.com/license"
                        }
                        
                        photo_details.append(photo_detail)
                        
                    except Exception as e:
                        logger.error(f"Error processing image: {str(e)}")
                        yield self.create_text_message(f"Failed to process image: {str(e)}")
            
            # Create JSON message with complete result data and photo details
            result = {
                'photos': photos,
                'error': None,
                'parameters': {
                    'query': query,
                    'count': count,
                    'orientation': orientation,
                    'color': color
                },
                'photo_details': photo_details
            }
            yield self.create_json_message(result)
            
            # Create variable messages for use in workflow
            yield self.create_variable_message('random_photos', photos)
            yield self.create_variable_message('photo_details', photo_details)
            
        except ValueError as e:
            # Parameter validation error
            error_message = f"Parameter error: {str(e)}"
            logger.error(error_message)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('random_photos', [])
            
        except requests.RequestException as e:
            # API request error
            error_message = f"Unsplash API request error: {str(e)}"
            logger.error(error_message)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('random_photos', [])
            
        except Exception as e:
            # Other unexpected errors
            error_message = f"Error retrieving random photos: {str(e)}"
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('random_photos', [])