from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get credentials
        redmine_host = self.runtime.credentials.get("redmine_host")
        api_key = self.runtime.credentials.get("api_key")

        if not redmine_host or not api_key:
            yield self.create_text_message("Error: Redmine host and API key are required")
            return

        # Remove trailing slash from host if present
        redmine_host = redmine_host.rstrip('/')

        # Get required parameter
        user_id = tool_parameters.get("user_id")
        if not user_id:
            yield self.create_text_message("Error: User ID is required")
            return

        # Validate user_id (should be numeric or 'current')
        if user_id != "current":
            try:
                int(user_id)
            except ValueError:
                yield self.create_text_message("Error: User ID must be numeric or 'current'")
                return

        # Build API URL
        api_url = f"{redmine_host}/users/{user_id}.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build query parameters
        params = {}

        # include
        include = tool_parameters.get("include")
        if include:
            # Validate include values
            valid_includes = ["memberships", "groups"]
            include_list = [item.strip() for item in include.split(",")]
            invalid_includes = [item for item in include_list if item not in valid_includes]
            
            if invalid_includes:
                yield self.create_text_message(f"Warning: Invalid include values: {', '.join(invalid_includes)}. Valid values are: {', '.join(valid_includes)}")
                # Filter out invalid includes
                include_list = [item for item in include_list if item in valid_includes]
            
            if include_list:
                params["include"] = ",".join(include_list)

        try:
            # Make API request
            response = requests.get(api_url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                # Success
                data = response.json()
                result = data

                # Output success message and JSON data
                user = data.get("user", {})
                user_id_resp = user.get("id", "N/A")
                user_login = user.get("login", "N/A")
                user_name = f"{user.get('firstname', '')} {user.get('lastname', '')}".strip()

                if user_name:
                    success_message = f"Retrieved user #{user_id_resp} - {user_login} ({user_name}) successfully"
                else:
                    success_message = f"Retrieved user #{user_id_resp} - {user_login} successfully"
                
                yield self.create_text_message(success_message)
                yield self.create_json_message(result)

            elif response.status_code == 404:
                if user_id == "current":
                    yield self.create_text_message("Error: Current user not found. Check your API key authentication")
                else:
                    yield self.create_text_message(f"Error: User #{user_id} not found or access denied")
                return

            elif response.status_code == 403:
                yield self.create_text_message("Error: Access denied. You may not have permission to view this user")
                return

            elif response.status_code == 401:
                yield self.create_text_message("Error: Authentication failed. Check your API key")
                return

            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error connecting to Redmine: {str(e)}")
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing Redmine response: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {str(e)}")