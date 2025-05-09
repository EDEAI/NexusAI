import os
import base64
import json
import uuid
import datetime
from typing import List, Optional, Union, Dict, Any, Tuple

from openai import OpenAI
from config import settings


class ImageGeneration:
    """
    A class that handles AI-powered image generation, editing, and variation creation.
    """

    def __init__(self, supplier: str, config: dict):
        """
        Initializes an ImageGeneration object with a supplier and configuration dictionary.

        :param supplier: str, the name of the image generation service provider.
        :param config: dict, a dictionary of configuration options for the supplier.
        :raises ValueError: If the supplier is not supported.
        """
        self.supplier = supplier
        self.config = config
        
        if self.supplier == 'OpenAI':
            self.client = OpenAI(**config)
            self.storage_url = settings.STORAGE_URL
        else:
            raise ValueError(f"Unsupported supplier: {supplier}")

    def _create_storage_directory(self) -> Tuple[str, str]:
        """
        Creates a year/month/day directory structure for storing images.
        
        :return: Tuple[str, str], containing:
            - relative_dir: str, the relative directory path
            - storage_dir: str, the absolute directory path
        """
        # Get current date for directory structure
        now = datetime.datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")
        day = now.strftime("%d")
        
        # Create directory structure for year/month/day
        relative_dir = os.path.join("ai_image", year, month, day)
        storage_dir = os.path.join(os.getcwd(), "storage", relative_dir)
        os.makedirs(storage_dir, exist_ok=True)
        
        return relative_dir, storage_dir

    def _process_openai_image_response(self, response, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes OpenAI API response data, saving images and generating response metadata.
        
        :param response: The complete response object from OpenAI API
        :param model_config: Dict[str, Any], optional configuration for image processing
        :return: Dict[str, Any], processed result containing:
            - images: List of image data with URLs and paths
            - usage: Token usage information
        """
        model_config = model_config or {}
        output_format = model_config.get("output_format", "png")
        
        # Create storage directory
        relative_dir, storage_dir = self._create_storage_directory()
        
        # Prepare response data
        result_data = []
        
        for image in response.data:
            item_data = {}
            
            if hasattr(image, 'url') and image.url:
                # If API returned a URL, use it directly
                item_data["url"] = image.url
                item_data["path"] = ""
            elif hasattr(image, 'b64_json') and image.b64_json:
                # If API returned base64 data, save it and create URL
                image_id = str(uuid.uuid4())
                filename = f"{image_id}.{output_format}"
                file_path = os.path.join(storage_dir, filename)
                relative_path = os.path.join(relative_dir, filename)
                
                # Save the image
                image_data = base64.b64decode(image.b64_json)
                with open(file_path, "wb") as f:
                    f.write(image_data)
                
                # Create URL from STORAGE_URL and path
                item_data["url"] = f"{self.storage_url}/file/{relative_path}"
                item_data["path"] = relative_path
            
            # Add any additional properties from the image response
            if hasattr(image, 'revised_prompt') and image.revised_prompt:
                item_data["revised_prompt"] = image.revised_prompt
            
            result_data.append(item_data)
        
        # Process token usage information
        usage_data = {
            "total_tokens": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "text_tokens": 0,
            "image_tokens": 0
        }
        
        if hasattr(response, 'usage'):
            # Extract basic token usage
            usage = response.usage
            usage_data["total_tokens"] = getattr(usage, "total_tokens", 0)
            usage_data["input_tokens"] = getattr(usage, "input_tokens", 0)
            usage_data["output_tokens"] = getattr(usage, "output_tokens", 0)
            
            # Extract detailed token information if available
            if hasattr(usage, "input_tokens_details"):
                details = usage.input_tokens_details
                usage_data["text_tokens"] = getattr(details, "text_tokens", 0)
                usage_data["image_tokens"] = getattr(details, "image_tokens", 0)
        
        # Prepare final result with images and usage data
        result = {
            "images": result_data,
            "usage": usage_data
        }
        
        return result

    def generate_image(self, prompt: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generates one or more images based on the provided text prompt.
        
        :param prompt: str, the text description to generate an image from.
        :param model_config: Dict[str, Any], optional configuration for the image generation.
            Supports the following keys:
            - n: int, number of images to generate (default: 1)
            - size: str, size of the generated images (e.g., "1024x1024")
            - response_format: str, format of the response ("url" or "b64_json") (default: "b64_json")
            - output_format: str, file format for saved images (default: "png")
            - other model-specific parameters
        
        :return: Dict[str, Any], containing:
            - images: List of dictionaries, each containing:
              - url: str, the URL to access the image
              - path: str, the relative path where the image is stored locally
              - revised_prompt: str, optional, the prompt after revision by the model
            - usage: Dict, token usage information including total_tokens, input_tokens, etc.

        :raises ValueError: If the supplier is not supported.
        """
        if self.supplier == 'OpenAI':
            model_config = model_config or {}
            response = self.client.images.generate(
                prompt=prompt,
                **model_config
            )
            
            return self._process_openai_image_response(response, model_config)
        else:
            raise ValueError(f"Unsupported supplier: {self.supplier}")

    def edit_image(self, image_path: Union[str, List[str]], prompt: str = "", mask_path: Optional[str] = None, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Edits an existing image by applying changes described in the prompt, optionally using a mask.
        
        :param image_path: Union[str, List[str]], path(s) to the source image(s) to be edited.
        :param prompt: str, a text description of the desired edits to the image.
        :param mask_path: Optional[str], path to a mask image where the masked (non-black) areas will be edited.
            If not provided, the entire image may be subject to edits.
        :param model_config: Dict[str, Any], optional configuration for the image editing.
            Supports the following keys:
            - n: int, number of edited images to generate (default: 1)
            - size: str, size of the output images
            - response_format: str, format of the response ("url" or "b64_json") (default: "b64_json")
            - output_format: str, file format for saved images (default: "png")
            - other model-specific parameters
        
        :return: Dict[str, Any], containing:
            - images: List of dictionaries, each containing:
              - url: str, the URL to access the edited image
              - path: str, the relative path where the edited image is stored locally
            - usage: Dict, token usage information including total_tokens, input_tokens, etc.
        
        :raises ValueError: If the supplier is not supported.
        :raises FileNotFoundError: If the image_path or mask_path don't exist.
        """
        if self.supplier == 'OpenAI':
            model_config = model_config or {}
            
            # Filter model_config to only include parameters supported by the edit API
            # Define allowed parameters for image editing
            allowed_params = {"background", "model", "n", "quality", "response_format", "size", "user"}
            
            # Create a filtered config with only allowed parameters if they exist in model_config
            filtered_model_config = {}
            for param in allowed_params:
                if param in model_config:
                    filtered_model_config[param] = model_config[param]
            
            # Convert single path to list for consistent processing
            image_paths = [image_path] if isinstance(image_path, str) else image_path
            
            if not image_paths:
                raise ValueError("At least one image path must be provided")
            
            # Check if using DALL-E-2 model
            is_dalle2 = filtered_model_config.get("model") == "dall-e-2"
            
            # For DALL-E-2, only use the first image
            if is_dalle2 and len(image_paths) > 1:
                print(f"Note: DALL-E-2 model only supports one input image. Using only the first image: {image_paths[0]}")
                image_paths = [image_paths[0]]
            
            try:
                # For DALL-E-2, only process the first image
                if is_dalle2:
                    if mask_path:
                        with open(image_paths[0], "rb") as image_file, open(mask_path, "rb") as mask_file:
                            response = self.client.images.edit(
                                image=image_file,
                                mask=mask_file,
                                prompt=prompt,
                                **filtered_model_config
                            )
                    else:
                        with open(image_paths[0], "rb") as image_file:
                            response = self.client.images.edit(
                                image=image_file,
                                prompt=prompt,
                                **filtered_model_config
                            )
                # For other models, process all images
                else:
                    # Note: OpenAI's current implementation may only support one image at a time
                    # This is a future-proof implementation for when multiple images are supported
                    image_files = []
                    try:
                        for path in image_paths:
                            image_files.append(open(path, "rb"))
                        
                        if mask_path:
                            with open(mask_path, "rb") as mask_file:
                                response = self.client.images.edit(
                                    image=image_files[0] if len(image_files) == 1 else image_files,
                                    mask=mask_file,
                                    prompt=prompt,
                                    **filtered_model_config
                                )
                        else:
                            response = self.client.images.edit(
                                image=image_files[0] if len(image_files) == 1 else image_files,
                                prompt=prompt,
                                **filtered_model_config
                            )
                    finally:
                        # Ensure all file handles are closed
                        for file in image_files:
                            file.close()
                
                return self._process_openai_image_response(response, model_config)
            except Exception as e:
                # Provide more detailed error information
                print(f"Error during image edit: {str(e)}")
                # Re-raise the exception after logging
                raise
        else:
            raise ValueError(f"Unsupported supplier: {self.supplier}")

    def create_image_variation(self, image_path: str, model_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Creates variations of a given input image, generating new images that are similar but distinct.
        
        :param image_path: str, path to the source image to create variations from.
        :param model_config: Dict[str, Any], optional configuration for the image variation generation.
            Supports the following keys:
            - n: int, number of variations to generate (default: 1)
            - size: str, size of the output images
            - response_format: str, format of the response ("url" or "b64_json") (default: "b64_json")
            - output_format: str, file format for saved images (default: "png")
            - other model-specific parameters
        
        :return: Dict[str, Any], containing:
            - images: List of dictionaries, each containing:
              - url: str, the URL to access the variation image
              - path: str, the relative path where the variation image is stored locally
            - usage: Dict, token usage information including total_tokens, input_tokens, etc.
        
        :raises ValueError: If the supplier is not supported.
        :raises FileNotFoundError: If the image_path doesn't exist.
        """
        if self.supplier == 'OpenAI':
            model_config = model_config or {}
            
            # Prepare the image file
            with open(image_path, "rb") as image_file:
                response = self.client.images.create_variation(
                    image=image_file,
                    **model_config
                )
            
            return self._process_openai_image_response(response, model_config)
        else:
            raise ValueError(f"Unsupported supplier: {self.supplier}") 