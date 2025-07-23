from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineUsersTool(Tool):
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
        api_url = f"{redmine_host}/users.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build query parameters following API documentation order
        params = {}

        # status
        status = tool_parameters.get("status")
        if status:
            try:
                status_int = int(status)
                if status_int in [1, 2, 3]:
                    params["status"] = status_int
                else:
                    yield self.create_text_message(f"Warning: Invalid status '{status}', must be 1 (Active), 2 (Registered), or 3 (Locked)")
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid status '{status}', must be numeric")

        # name
        name = tool_parameters.get("name")
        if name:
            params["name"] = name

        # group_id
        group_id = tool_parameters.get("group_id")
        if group_id:
            try:
                params["group_id"] = int(group_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid group_id '{group_id}', must be numeric")

        try:
            # Make API request
            response = requests.get(api_url, headers=headers, params=params, timeout=30)

            if response.status_code == 200:
                # Success
                data = response.json()
                result = data

                # Output success message and JSON data
                users = data.get("users", [])
                user_count = len(users)

                success_message = f"Retrieved {user_count} users successfully"
                yield self.create_text_message(success_message)
                yield self.create_json_message(result)

            elif response.status_code == 403:
                yield self.create_text_message("Error: Access denied. Admin privileges are required to list users")
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
