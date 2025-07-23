from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from drive_utils import GoogleDriveUtils


class GoogleDriveCreateFolder(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Create a folder in Google Drive
        """
        # Get parameters
        folder_name = tool_parameters.get("name", "")
        parent_id = tool_parameters.get("parent_id", "root")
        
        if not folder_name:
            yield self.create_text_message("Invalid parameter: folder name is required")
            return
            
        try:
            # Get credentials from the utility class
            credentials_json = self.runtime.credentials["credentials_json"]
            creds = GoogleDriveUtils.get_credentials(credentials_json)
            
            # Create the folder using the utility class
            folder = GoogleDriveUtils.create_folder(folder_name, parent_id, creds)

            result = {
                "id": folder.get("id"),
                "name": folder.get("name"),
                "parent_id": parent_id,
                "success": True,
                "web_view_link": folder.get("webViewLink", "")
            }
            yield self.create_text_message("Folder created successfully")
            yield self.create_json_message(result)
        except Exception as e:
            yield self.create_text_message(f"Error creating folder: {str(e)}")
