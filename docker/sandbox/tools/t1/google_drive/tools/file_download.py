from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from drive_utils import GoogleDriveUtils


class GoogleDriveFileDownload(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Download a file from Google Drive
        """
        file_id = tool_parameters.get("file_id", "")

        if not file_id:
            yield self.create_text_message("Invalid parameter: file_id is required")
            return

        try:
            # Get credentials from the utility class
            credentials_json = self.runtime.credentials["credentials_json"]
            credentials = GoogleDriveUtils.get_credentials(credentials_json)

            # Download the file using GoogleDriveUtils
            file_content, metadata = GoogleDriveUtils.download_file(
                file_id, credentials
            )

            if file_content is None:
                yield self.create_text_message(
                    f"Failed to download file with ID: {file_id}"
                )
                return

            # Create blob message with the downloaded content
            yield self.create_blob_message(file_content, metadata)

            # Prepare result with enhanced metadata
            result = {
                "file_id": file_id,
                "file_name": metadata.get("file_name", "unknown"),
                "mime_type": metadata.get("mime_type", "unknown"),
                "file_size": len(file_content),
                "exported": metadata.get("exported", False),
            }

            # Add original file info if it was exported
            if metadata.get("exported", False):
                result["original_name"] = metadata.get("original_name", "unknown")
                result["original_mime_type"] = metadata.get(
                    "original_mime_type", "unknown"
                )

            # Create success message with appropriate context
            if metadata.get("exported", False):
                success_message = (
                    f"Google Workspace file '{metadata.get('original_name', 'unknown')}' "
                    f"exported as PDF '{metadata.get('file_name', 'unknown')}' successfully"
                )
            else:
                success_message = f"File '{metadata.get('file_name', 'unknown')}' downloaded successfully"

            yield self.create_text_message(success_message)
            yield self.create_json_message(result)

        except Exception as e:
            yield self.create_text_message(f"Error downloading file: {str(e)}")
