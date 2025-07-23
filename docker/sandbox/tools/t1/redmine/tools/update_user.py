from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineUpdateUserTool(Tool):
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

        # Validate user ID is numeric
        try:
            int(user_id)
        except ValueError:
            yield self.create_text_message("Error: User ID must be a numeric value")
            return

        # Build API URL
        api_url = f"{redmine_host}/users/{user_id}.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build user data following API documentation order (same as create_user)
        user_data = {}
        has_updates = False

        # login
        login = tool_parameters.get("login")
        if login:
            user_data["login"] = login
            has_updates = True

        # password
        password = tool_parameters.get("password")
        if password:
            user_data["password"] = password
            has_updates = True

        # firstname
        firstname = tool_parameters.get("firstname")
        if firstname:
            user_data["firstname"] = firstname
            has_updates = True

        # lastname
        lastname = tool_parameters.get("lastname")
        if lastname:
            user_data["lastname"] = lastname
            has_updates = True

        # mail
        mail = tool_parameters.get("mail")
        if mail:
            user_data["mail"] = mail
            has_updates = True

        # auth_source_id
        auth_source_id = tool_parameters.get("auth_source_id")
        if auth_source_id:
            try:
                user_data["auth_source_id"] = int(auth_source_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid auth_source_id '{auth_source_id}', must be numeric")

        # mail_notification
        mail_notification = tool_parameters.get("mail_notification")
        if mail_notification:
            valid_notifications = ["only_my_events", "none", "all", "selected", "only_assigned", "only_owner"]
            if mail_notification in valid_notifications:
                user_data["mail_notification"] = mail_notification
                has_updates = True
            else:
                yield self.create_text_message(f"Warning: Invalid mail_notification '{mail_notification}', must be one of: {', '.join(valid_notifications)}")

        # must_change_passwd
        must_change_passwd = tool_parameters.get("must_change_passwd")
        if must_change_passwd is not None:
            user_data["must_change_passwd"] = bool(must_change_passwd)
            has_updates = True

        # generate_password
        generate_password = tool_parameters.get("generate_password")
        if generate_password is not None:
            user_data["generate_password"] = bool(generate_password)
            has_updates = True

        # custom_fields
        custom_fields = tool_parameters.get("custom_fields")
        if custom_fields:
            try:
                custom_fields_data = json.loads(custom_fields)
                if isinstance(custom_fields_data, list):
                    user_data["custom_fields"] = custom_fields_data
                    has_updates = True
                else:
                    yield self.create_text_message("Warning: custom_fields must be a JSON array")
            except json.JSONDecodeError:
                yield self.create_text_message("Warning: Invalid custom_fields JSON format")

        if not has_updates:
            # Check for admin parameter which is handled separately
            admin = tool_parameters.get("admin")
            if admin is None:
                yield self.create_text_message("Error: No parameters provided for update. At least one field must be specified.")
                return

        # Prepare request payload
        payload: dict[str, Any] = {}

        if user_data:
            payload["user"] = user_data

        # admin (top-level parameter, not inside user)
        admin = tool_parameters.get("admin")
        if admin is not None:
            payload["admin"] = False

        # Ensure we have something to update
        if not payload:
            yield self.create_text_message("Error: No parameters provided for update. At least one field must be specified.")
            return

        try:
            # Make API request
            response = requests.put(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                # Success - user updated
                success_message = f"User #{user_id} updated successfully"
                yield self.create_text_message(success_message)

                # Try to get the updated user details
                try:
                    get_response = requests.get(api_url, headers=headers, timeout=30)
                    if get_response.status_code == 200:
                        updated_data = get_response.json()
                        yield self.create_json_message(updated_data)
                    else:
                        updated_fields = []
                        if user_data:
                            updated_fields.extend(list(user_data.keys()))
                        if admin is not None:
                            updated_fields.append("admin")
                        yield self.create_json_message({"message": f"User #{user_id} updated successfully", "updated_fields": updated_fields})
                except:
                    updated_fields = []
                    if user_data:
                        updated_fields.extend(list(user_data.keys()))
                    if admin is not None:
                        updated_fields.append("admin")
                    yield self.create_json_message({"message": f"User #{user_id} updated successfully", "updated_fields": updated_fields})

            elif response.status_code == 422:
                # Validation errors
                try:
                    error_data = response.json()
                    errors = error_data.get("errors", [])
                    if errors:
                        error_message = "Validation errors:\n" + "\n".join([f"- {error}" for error in errors])
                        yield self.create_text_message(error_message)
                    else:
                        yield self.create_text_message("Validation error occurred but no details provided")
                except json.JSONDecodeError:
                    yield self.create_text_message("Validation error occurred")
                return

            elif response.status_code == 403:
                yield self.create_text_message("Error: Access denied. Admin privileges are required to update users")
                return

            elif response.status_code == 404:
                yield self.create_text_message(f"Error: User #{user_id} not found")
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
