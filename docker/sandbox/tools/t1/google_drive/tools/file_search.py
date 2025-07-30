import json
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from drive_utils import GoogleDriveUtils


class GoogleDriveFileSearch(Tool):

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Search for files in Google Drive
        """
        query = tool_parameters.get("query", "")
        parent_id = tool_parameters.get("parent_id", None)
        file_type = tool_parameters.get("file_type", None)

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
            
            # Search files using the utility class
            files = GoogleDriveUtils.search_files(query, max_results, creds, parent_id, file_type)
            
            if not files:
                yield self.create_text_message(f"No files found matching '{query}'")
                return
                
            result = {
                "file_count": len(files),
                "files": [
                    {
                        "name": file["name"],
                        "id": file["id"],
                        "parent_id": file["parent_id"],
                        "mime_type": file["mime_type"]
                    } for file in files
                ]
            }

            yield self.create_text_message("Files found successfully")
            yield self.create_json_message(result)
        except Exception as e:
            yield self.create_text_message(f"Error searching files: {str(e)}")
