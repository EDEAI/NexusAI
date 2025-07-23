import base64
import logging
from collections.abc import Generator
from typing import Any
from urllib.parse import urlencode

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.config.logger_format import plugin_logger_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class MermaidConverterTool(Tool):
    """
    Converts Mermaid diagram code to images using the mermaid.ink API service.
    
    Supports multiple output formats: PNG, JPG, SVG, PDF
    Includes theme support and customization options.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Convert Mermaid diagram code to image.
        
        Args:
            tool_parameters: Dictionary containing:
                - mermaid_code (str, required): The Mermaid diagram syntax
                - output_format (str, optional): png/jpg/svg/pdf, default 'png'
                - theme (str, optional): default/dark/neutral/forest, default 'default'
                - background_color (str, optional): hex color for background
                - width (int, optional): image width in pixels
                - height (int, optional): image height in pixels
                
        Yields:
            ToolInvokeMessage: Blob message with converted image or text message with error
        """
        try:
            # PATTERN: Always validate input first
            mermaid_code = tool_parameters.get("mermaid_code", "").strip()

            # Strip markdown code block fences
            mermaid_code = mermaid_code.replace("```mermaid", "").replace("```", "").strip()
            
            if not mermaid_code:
                yield self.create_text_message("Error: Mermaid code is required and cannot be empty")
                return
            
            # Extract parameters with defaults
            output_format = tool_parameters.get("output_format", "png").lower()
            theme = tool_parameters.get("theme", "default")
            background_color = tool_parameters.get("background_color", "")
            width = tool_parameters.get("width")
            height = tool_parameters.get("height")
            
            # Validate output format
            valid_formats = ["png", "jpg", "jpeg", "svg", "pdf"]
            if output_format not in valid_formats:
                yield self.create_text_message(f"Error: Invalid output format '{output_format}'. Supported formats: {', '.join(valid_formats)}")
                return
            
            logger.info(f"Converting Mermaid diagram to {output_format} format")
            
            # CRITICAL: Base64 encode the mermaid code
            try:
                encoded_diagram = base64.urlsafe_b64encode(mermaid_code.encode('utf-8')).decode('ascii')
            except Exception as e:
                yield self.create_text_message(f"Error: Failed to encode diagram: {str(e)}")
                return
            
            # PATTERN: Build URL based on format
            url = self._build_api_url(encoded_diagram, output_format, theme, background_color, width, height)
            
            logger.info(f"Making request to {url}")
            
            # CRITICAL: HTTP request with timeout
            try:
                response = requests.get(url)
                
                if response.status_code != 200:
                    if response.status_code == 400:
                        error_msg = f"Invalid Mermaid syntax: {response.text}"
                    elif response.status_code == 413:
                        error_msg = "Diagram too large for API"
                    else:
                        error_msg = f"Conversion failed: HTTP {response.status_code}"
                    
                    logger.error(error_msg)
                    yield self.create_text_message(error_msg)
                    return
                    
                # PATTERN: Determine mime type based on format
                mime_types = {
                    "png": "image/png",
                    "jpg": "image/jpeg", 
                    "jpeg": "image/jpeg",
                    "svg": "image/svg+xml",
                    "pdf": "application/pdf"
                }
                
                mime_type = mime_types.get(output_format, "image/png")
                filename = f"mermaid_diagram.{output_format}"
                
                # CRITICAL: Return as blob message with proper metadata
                yield self.create_blob_message(
                    blob=response.content,
                    meta={"mime_type": mime_type, "file_name": filename}
                )
                
                logger.info(f"Successfully converted diagram to {output_format} ({len(response.content)} bytes)")
                
            except requests.Timeout:
                error_msg = "Conversion timeout - mermaid.ink took too long to respond"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                
            except requests.ConnectionError as e:
                error_msg = f"Connection error: Unable to reach mermaid.ink service"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                
            except Exception as e:
                error_msg = f"Request error: {str(e)}"
                logger.error(error_msg)
                yield self.create_text_message(error_msg)
                
        except Exception as e:
            error_msg = f"Unexpected error during conversion: {str(e)}"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
    
    def _build_api_url(self, encoded_diagram: str, output_format: str, theme: str, 
                      background_color: str, width: int = None, height: int = None) -> str:
        """
        Build the mermaid.ink API URL with proper parameters.
        
        Args:
            encoded_diagram: Base64 encoded mermaid code
            output_format: Target format (png/jpg/svg/pdf)
            theme: Visual theme
            background_color: Background color
            width: Image width
            height: Image height
            
        Returns:
            Complete API URL with parameters
        """
        # GOTCHA: Different endpoints for different formats
        if output_format == "svg":
            base_url = f"https://mermaid.ink/svg/{encoded_diagram}"
        elif output_format == "pdf":
            base_url = f"https://mermaid.ink/pdf/{encoded_diagram}"
        else:  # png, jpg, jpeg
            base_url = f"https://mermaid.ink/img/{encoded_diagram}"
        
        # Build query parameters
        params = {}
        
        # Format-specific parameters
        if output_format in ["png", "jpg", "jpeg"]:
            params["type"] = output_format
            
        # Theme parameter (only for image formats, not SVG/PDF)
        if theme and theme != "default" and output_format in ["png", "jpg", "jpeg"]:
            params["theme"] = theme
        
        # Background color parameter
        if background_color:
            # Support both hex colors (FF0000) and named colors (!white)
            if background_color.startswith("!"):
                params["bgColor"] = background_color
            else:
                # Remove # if present and ensure it's a valid hex color
                color = background_color.lstrip("#")
                if len(color) == 6 and all(c in "0123456789ABCDEFabcdef" for c in color):
                    params["bgColor"] = color
        
        # Size parameters
        if width:
            params["width"] = str(width)
        if height:
            params["height"] = str(height)
        
        # Combine URL with parameters
        if params:
            return f"{base_url}?{urlencode(params)}"
        else:
            return base_url