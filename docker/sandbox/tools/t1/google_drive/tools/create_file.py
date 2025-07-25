from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from drive_utils import GoogleDriveUtils


class GoogleDriveCreateFile(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a file in Google Drive
        """
        # Get parameters
        file_data = tool_parameters.get("file", {})
        file_name = tool_parameters.get("name", "")
        parent_id = tool_parameters.get("parent_id", "root")
        folder_name = tool_parameters.get("folder_name", "")
        
        # Debug print
        print(f"File data type: {type(file_data)}")
        print(f"File data: {file_data}")
        
        # Initialize variables
        file_url = ""
        mime_type = ""
        
        # If file data is provided, use its information
        if file_data:
            # Check if file_data is a dictionary or an object
            if isinstance(file_data, dict):
                # Dictionary access
                if not file_name and 'filename' in file_data:
                    file_name = file_data.get('filename')
                
                mime_type = file_data.get('mime_type', '')
                file_url = file_data.get('url', '')
            else:
                # Object attribute access
                try:
                    if not file_name and hasattr(file_data, 'filename'):
                        file_name = file_data.filename
                    
                    if hasattr(file_data, 'mime_type'):
                        mime_type = file_data.mime_type
                        
                    file_url = getattr(file_data, 'url', '')
                except Exception as e:
                    print(f"Error accessing file data attributes: {str(e)}")
                    # Try direct access for common attributes
                    if not file_name:
                        file_name = str(getattr(file_data, 'filename', ''))
                    mime_type = str(getattr(file_data, 'mime_type', ''))
                    file_url = str(getattr(file_data, 'url', ''))
                    
            if not file_url:
                yield self.create_text_message("Error: No file URL provided in file data")
                return
        else:
            yield self.create_text_message("Error: No file data provided")
            return
            
        try:
            # Get credentials from the utility class
            credentials_json = self.runtime.credentials["credentials_json"]
            creds = GoogleDriveUtils.get_credentials(credentials_json)
            
            # Handle folder_name if provided (prioritize over parent_id)
            if folder_name:
                print(f"Checking for folder: {folder_name}")
                folder_id = GoogleDriveUtils.find_folder_by_name(folder_name, creds, parent_id)
                
                if folder_id:
                    print(f"Found existing folder: {folder_name} with ID: {folder_id}")
                    parent_id = folder_id
                else:
                    print(f"Folder not found, creating new folder: {folder_name}")
                    # Create the folder
                    folder = GoogleDriveUtils.create_folder(folder_name, parent_id, creds)
                    if folder:
                        parent_id = folder.get("id")
                        print(f"Created new folder with ID: {parent_id}")
                    else:
                        yield self.create_text_message(f"Error creating folder: {folder_name}")
                        return
        
            # Override with explicitly provided mime_type if available
            if tool_parameters.get("mime_type"):
                mime_type = tool_parameters.get("mime_type")
                print(f"Overriding mime_type with explicitly provided value: {mime_type}")
            
            if not file_name:
                yield self.create_text_message("Invalid parameter: file name is required")
                return
                
            if not mime_type:
                # Default to application/octet-stream if mime_type not provided
                mime_type = "application/octet-stream"
                print(f"No mime_type detected, using default: {mime_type}")
            
            # Download file content from URL
            try:
                # Check if URL starts with /files and prepend appropriate URL
                download_url = file_url
                if file_url.startswith('/files'):
                    # For Docker environment: use api service name instead of localhost
                    # This assumes plugin is running in the same Docker network as Dify
                    download_url = f"http://api:5001{file_url}"
                    print(f"URL starts with /files, using Docker network URL: {download_url}")
                
                print(f"Downloading file from URL: {download_url}")
                response = requests.get(download_url)
                response.raise_for_status()  # Raise exception for non-200 status codes
                file_content = response.content
                print(f"Downloaded file content: {len(file_content)} bytes")
            except Exception as e:
                yield self.create_text_message(f"Error downloading file from URL: {str(e)}")
                return
            
            # Create the file using the utility class
            file = GoogleDriveUtils.create_file(file_name, parent_id, mime_type, file_content, creds)
            
            result = {
                "id": file.get("id"),
                "name": file.get("name"),
                "parent_id": parent_id,
                "mime_type": mime_type,
                "success": True,
                "web_view_link": file.get("webViewLink", "")
            }
            
            # Add folder information if folder was used
            if folder_name:
                result["folder_name"] = folder_name
                
            yield self.create_text_message("File created successfully")
            yield self.create_json_message(result)
        except Exception as e:
            yield self.create_text_message(f"Error creating file: {str(e)}")
