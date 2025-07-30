from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineIssueTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get credentials
        redmine_host = self.runtime.credentials.get("redmine_host")
        api_key = self.runtime.credentials.get("api_key")

        if not redmine_host or not api_key:
            yield self.create_text_message("Error: Redmine host and API key are required")
            return

        # Remove trailing slash from host if present
        redmine_host = redmine_host.rstrip('/')

        # Get issue ID
        issue_id = tool_parameters.get("issue_id")
        if not issue_id:
            yield self.create_text_message("Error: Issue ID is required")
            return

        # Validate issue ID is numeric
        try:
            int(issue_id)
        except ValueError:
            yield self.create_text_message("Error: Issue ID must be a numeric value")
            return

        # Build API URL
        api_url = f"{redmine_host}/issues/{issue_id}.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build query parameters
        params = {}

        include_param = tool_parameters.get("include")
        if include_param:
            # Validate include parameter values
            valid_includes = ["journals", "children", "attachments", "relations", "changesets", "watchers"]
            include_list = [item.strip() for item in include_param.split(",")]
            invalid_includes = [item for item in include_list if item not in valid_includes]

            if invalid_includes:
                yield self.create_text_message(f"Warning: Invalid include parameters ignored: {', '.join(invalid_includes)}")
                include_list = [item for item in include_list if item in valid_includes]

            if include_list:
                params["include"] = ",".join(include_list)

        try:
            # Make API request
            response = requests.get(api_url, headers=headers, params=params, timeout=30)

            if response.status_code == 404:
                yield self.create_text_message(f"Error: Issue #{issue_id} not found")
                return
            elif response.status_code == 403:
                yield self.create_text_message("Error: Access denied. Check your API key permissions")
                return

            response.raise_for_status()

            data = response.json()
            issue = data.get("issue", {})

            if not issue:
                yield self.create_text_message(f"Error: No issue data returned for ID #{issue_id}")
                return

            result = {
                "issue": issue
            }

            # Download and output attachments if requested
            if "attachments" in params.get("include", "") and issue.get("attachments"):
                for attachment in issue["attachments"]:
                    content_url = attachment.get("content_url")
                    if content_url:
                        try:
                            attachment_response = requests.get(content_url, headers=headers, timeout=30)
                            attachment_response.raise_for_status()

                            yield self.create_blob_message(
                                blob=attachment_response.content,
                                meta={
                                    "mime_type": attachment.get("content_type", "application/octet-stream"),
                                    "filename": attachment.get("filename", f"attachment_{attachment.get('id')}")
                                }
                            )
                        except requests.exceptions.RequestException as e:
                            yield self.create_text_message(f"Error downloading attachment {attachment.get('filename', attachment.get('id'))}: {str(e)}")

            # Output JSON as text string
            yield self.create_text_message(json.dumps(result, ensure_ascii=False))
            yield self.create_json_message(result)

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error connecting to Redmine: {str(e)}")
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing Redmine response: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {str(e)}")
