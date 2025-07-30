from collections.abc import Generator
from typing import Any
import requests
import json
import mimetypes

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get credentials
        redmine_host = self.runtime.credentials.get("redmine_host")
        api_key = self.runtime.credentials.get("api_key")

        if not redmine_host or not api_key:
            yield self.create_text_message("Error: Redmine host and API key are required")
            return

        # Remove trailing slash from host if present
        redmine_host = redmine_host.rstrip('/')

        # Build API URL
        api_url = f"{redmine_host}/issues.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build query parameters following API documentation order
        params = {}

        # Basic parameters (offset, limit, sort, include)
        if tool_parameters.get("offset"):
            try:
                offset_int = int(tool_parameters["offset"])
                if offset_int >= 0:
                    params["offset"] = str(offset_int)
            except ValueError:
                pass

        # Set limit (default 25, max 100)
        limit = tool_parameters.get("limit", "25")
        try:
            limit_int = int(limit)
            if limit_int > 100:
                limit_int = 100
            elif limit_int < 1:
                limit_int = 25
            params["limit"] = str(limit_int)
        except ValueError:
            params["limit"] = "25"

        if tool_parameters.get("sort"):
            params["sort"] = tool_parameters["sort"]

        if tool_parameters.get("include"):
            params["include"] = tool_parameters["include"]

        # Optional filters (issue_id, project_id, subproject_id, tracker_id, status_id, assigned_to_id, parent_id)
        if tool_parameters.get("issue_id"):
            params["issue_id"] = tool_parameters["issue_id"]

        if tool_parameters.get("project_id"):
            params["project_id"] = tool_parameters["project_id"]

        if tool_parameters.get("subproject_id"):
            params["subproject_id"] = tool_parameters["subproject_id"]

        if tool_parameters.get("tracker_id"):
            params["tracker_id"] = tool_parameters["tracker_id"]

        if tool_parameters.get("status_id"):
            params["status_id"] = tool_parameters["status_id"]

        if tool_parameters.get("assigned_to_id"):
            params["assigned_to_id"] = tool_parameters["assigned_to_id"]

        if tool_parameters.get("parent_id"):
            params["parent_id"] = tool_parameters["parent_id"]

        # Date filters
        if tool_parameters.get("created_on"):
            params["created_on"] = tool_parameters["created_on"]

        if tool_parameters.get("updated_on"):
            params["updated_on"] = tool_parameters["updated_on"]

        # Handle additional query parameters (custom fields and other filters)
        if tool_parameters.get("custom_fields"):
            custom_fields_str = tool_parameters["custom_fields"]
            # Parse additional parameters in format: cf_1=value&fixed_version_id=2&category_id=3
            if custom_fields_str:
                try:
                    # Split by & and add each parameter
                    for field_param in custom_fields_str.split('&'):
                        if '=' in field_param:
                            key, value = field_param.split('=', 1)
                            key = key.strip()
                            value = value.strip()
                            # Accept any parameter (custom fields, fixed_version_id, category_id, etc.)
                            if key and value:
                                params[key] = value
                except (ValueError, AttributeError):
                    # Ignore malformed parameters
                    pass

        try:
            # Make API request
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check if attachments should be downloaded
            include_param = tool_parameters.get("include", "")
            should_download_attachments = "attachments" in include_param.lower()

            # Download attachments if requested
            if should_download_attachments and "issues" in data:
                for issue in data["issues"]:
                    if "attachments" in issue and issue["attachments"]:
                        for attachment in issue["attachments"]:
                            try:
                                # Download attachment
                                attachment_url = f"{redmine_host}/attachments/download/{attachment['id']}/{attachment['filename']}"
                                attachment_response = requests.get(
                                    attachment_url,
                                    headers={"X-Redmine-API-Key": api_key},
                                    timeout=30
                                )
                                attachment_response.raise_for_status()

                                # Determine MIME type
                                mime_type = attachment.get('content_type', 'application/octet-stream')
                                if not mime_type:
                                    mime_type, _ = mimetypes.guess_type(attachment['filename'])
                                    if not mime_type:
                                        mime_type = 'application/octet-stream'

                                # Create blob message for the attachment
                                yield self.create_blob_message(
                                    blob=attachment_response.content,
                                    meta={
                                        'mime_type': mime_type,
                                        'filename': attachment['filename']
                                    }
                                )
                            except (requests.exceptions.RequestException, ValueError):
                                # Continue if attachment download fails
                                continue

            # Output JSON as text string
            yield self.create_text_message(json.dumps(data, ensure_ascii=False))
            yield self.create_json_message(data)

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error connecting to Redmine: {str(e)}")
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing Redmine response: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {str(e)}")
