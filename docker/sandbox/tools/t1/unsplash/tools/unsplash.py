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

class UnsplashTool(Tool):
    """Unsplash Search Tool
    Provides Unsplash image search functionality
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
        # Validate required parameters
        query = tool_parameters.get('query')
        if not query or not isinstance(query, str) or len(query.strip()) == 0:
            raise ValueError("Search query cannot be empty")
        
        # Validate page and results per page
        per_page = tool_parameters.get('per_page', 10)
        if not isinstance(per_page, (int, float)) or per_page <= 0 or per_page > 30:
            raise ValueError("Results per page must be an integer between 1 and 30")
    
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
        """Execute Unsplash image search
        
        Args:
            tool_parameters: Search parameters
            
        Yields:
            ToolInvokeMessage: Tool invocation messages
        """
        try:
            # Validate parameters
            self._validate_parameters(tool_parameters)
            
            # Get parameters
            query = tool_parameters.get('query')
            per_page = min(int(tool_parameters.get('per_page', 10)), 30)
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
            url = urljoin(self.API_BASE_URL, '/search/photos')
            params = {
                'query': query,
                'per_page': per_page,
                'page': 1
            }
            
            # Add optional parameters
            if orientation:
                params['orientation'] = orientation
            if color:
                params['color'] = color
            
            logger.info(f"Searching Unsplash with parameters: {params}")
            
            # Send API request
            start_time = time.time()
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            request_time = time.time() - start_time
            
            logger.info(f"Unsplash API request completed in {request_time:.2f} seconds")
            
            # Process response data
            results = data.get('results', [])
            total = data.get('total', 0)
            total_pages = data.get('total_pages', 0)
            
            # Create text message with search results summary
            search_params = f"query='{query}'"
            if orientation:
                search_params += f", orientation='{orientation}'"
            if color:
                search_params += f", color='{color}'"
                
            if total > 0:
                summary_text = f"Found {total} photos for {search_params}. Showing {len(results)} results."
            else:
                summary_text = f"No photos found for {search_params}. Please try different keywords."
            
            # Only output brief summary to text
            yield self.create_text_message(summary_text)
            
            # Handle case with no results
            if not results:
                yield self.create_json_message({
                    'photos': [],
                    'total': 0,
                    'total_pages': 0,
                    'error': None,
                    'search_parameters': {
                        'query': query,
                        'per_page': per_page,
                        'orientation': orientation,
                        'color': color
                    }
                })
                yield self.create_variable_message('photos', [])
                yield self.create_variable_message('total_results', 0)
                return
            
            # Build return results
            photos = []
            photo_details = []
            
            for photo in results:
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
                        filename = f"unsplash_{photo_id}.jpg"
                        
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
            
            # Create JSON message with complete search result data and photo details
            result = {
                'photos': photos,
                'total': total,
                'total_pages': total_pages,
                'error': None,
                'search_parameters': {
                    'query': query,
                    'per_page': per_page,
                    'orientation': orientation,
                    'color': color
                },
                'photo_details': photo_details
            }
            yield self.create_json_message(result)
            
            # Create variable messages for use in workflow
            yield self.create_variable_message('photos', photos)
            yield self.create_variable_message('photo_details', photo_details)
            yield self.create_variable_message('total_results', total)
            
        except ValueError as e:
            # Parameter validation error
            error_message = f"Parameter error: {str(e)}"
            logger.error(error_message)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('photos', [])
            yield self.create_variable_message('total_results', 0)
            
        except requests.RequestException as e:
            # API request error
            error_message = f"Unsplash API request error: {str(e)}"
            logger.error(error_message)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('photos', [])
            yield self.create_variable_message('total_results', 0)
            
        except Exception as e:
            # Other unexpected errors
            error_message = f"Error searching Unsplash: {str(e)}"
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            yield self.create_text_message(error_message)
            yield self.create_json_message({'error': error_message})
            yield self.create_variable_message('photos', [])
            yield self.create_variable_message('total_results', 0)
