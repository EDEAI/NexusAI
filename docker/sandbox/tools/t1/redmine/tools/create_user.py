from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineCreateUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get credentials
        redmine_host = self.runtime.credentials.get("redmine_host")
        api_key = self.runtime.credentials.get("api_key")

        if not redmine_host or not api_key:
            yield self.create_text_message("Error: Redmine host and API key are required")
            return

        # Remove trailing slash from host if present
        redmine_host = redmine_host.rstrip('/')

        # Get required parameters
        login = tool_parameters.get("login")
        firstname = tool_parameters.get("firstname")
        lastname = tool_parameters.get("lastname")
        mail = tool_parameters.get("mail")

        if not login:
            yield self.create_text_message("Error: Login is required")
            return

        if not firstname:
            yield self.create_text_message("Error: First name is required")
            return

        if not lastname:
            yield self.create_text_message("Error: Last name is required")
            return

        if not mail:
            yield self.create_text_message("Error: Email is required")
            return

        # Build API URL
        api_url = f"{redmine_host}/users.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build user data following API documentation exact order
        user_data = {
            "login": login,
        }

        # password
        password = tool_parameters.get("password")
        if password:
            user_data["password"] = password

        # firstname (required)
        user_data["firstname"] = firstname

        # lastname (required)
        user_data["lastname"] = lastname

        # mail (required)
        user_data["mail"] = mail

        # auth_source_id
        auth_source_id = tool_parameters.get("auth_source_id")
        if auth_source_id:
            try:
                user_data["auth_source_id"] = int(auth_source_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid auth_source_id '{auth_source_id}', must be numeric")

        # mail_notification
        mail_notification = tool_parameters.get("mail_notification")
        if mail_notification:
            valid_notifications = ["only_my_events", "none", "all", "selected", "only_assigned", "only_owner"]
            if mail_notification in valid_notifications:
                user_data["mail_notification"] = mail_notification
            else:
                yield self.create_text_message(f"Warning: Invalid mail_notification '{mail_notification}', must be one of: {', '.join(valid_notifications)}")

        # must_change_passwd
        must_change_passwd = tool_parameters.get("must_change_passwd")
        if must_change_passwd is not None:
            user_data["must_change_passwd"] = bool(must_change_passwd)

        # generate_password
        generate_password = tool_parameters.get("generate_password")
        if generate_password is not None:
            user_data["generate_password"] = bool(generate_password)

        # custom_fields
        custom_fields = tool_parameters.get("custom_fields")
        if custom_fields:
            try:
                custom_fields_data = json.loads(custom_fields)
                if isinstance(custom_fields_data, list):
                    user_data["custom_fields"] = custom_fields_data
                else:
                    yield self.create_text_message("Warning: custom_fields must be a JSON array")
            except json.JSONDecodeError:
                yield self.create_text_message("Warning: Invalid custom_fields JSON format")

        # Prepare request payload
        payload: dict[str, Any] = {
            "user": user_data
        }

        # send_information (top-level parameter, not inside user)
        send_information = tool_parameters.get("send_information")
        if send_information is not None:
            payload["send_information"] = bool(send_information)

        try:
            # Make API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 201:
                # Success - user created
                data = response.json()
                result = data

                # Output success message and JSON data
                created_user = data.get("user", {})
                user_id = created_user.get("id")
                user_login = created_user.get("login")
                user_name = f"{created_user.get('firstname', '')} {created_user.get('lastname', '')}"

                success_message = f"User created successfully: #{user_id} - {user_login} ({user_name.strip()})"
                yield self.create_text_message(success_message)
                yield self.create_json_message(result)

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
                yield self.create_text_message("Error: Access denied. Admin privileges are required to create users")
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
