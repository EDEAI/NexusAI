import json
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from drive_utils import GoogleDriveUtils


class GoogleDriveFolderSearch(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for folders in Google Drive
        """
        query = tool_parameters.get("query", "")
        parent_id = tool_parameters.get("parent_id", None)

        if not query:
            yield self.create_text_message("Invalid parameter: search query is required")
            return
            
        max_results = tool_parameters.get("max_results", 10)
        try:
            max_results = int(max_results)
        except ValueError:
            max_results = 10
            
        try:
            # Get credentials from the utility class
            credentials_json = self.runtime.credentials["credentials_json"]
            creds = GoogleDriveUtils.get_credentials(credentials_json)
            
            # Use the folder type parameter to limit search to folders only
            folders = GoogleDriveUtils.search_files(query, max_results, creds, parent_id, "folder")
            
            if not folders:
                yield self.create_text_message(f"No folders found matching '{query}'")
                return
                
            result = {
                "folder_count": len(folders),
                "folders": [
                    {
                        "name": folder["name"],
                        "id": folder["id"],
                        "parent_id": folder["parent_id"]
                    } for folder in folders
                ]
            }
            yield self.create_text_message("Folders found successfully")
            yield self.create_json_message(result)
        except Exception as e:
            yield self.create_text_message(f"Error searching folders: {str(e)}")
