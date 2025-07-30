from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineCreateIssueTool(Tool):
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
        project_id = tool_parameters.get("project_id")
        subject = tool_parameters.get("subject")

        if not project_id:
            yield self.create_text_message("Error: Project ID is required")
            return

        if not subject:
            yield self.create_text_message("Error: Subject is required")
            return

        # Build API URL
        api_url = f"{redmine_host}/issues.json"

        # Prepare headers
        headers = {
            "X-Redmine-API-Key": api_key,
            "Content-Type": "application/json"
        }

        # Build issue data following API documentation exact order
        issue_data = {
            "project_id": project_id,
        }

        # tracker_id
        tracker_id = tool_parameters.get("tracker_id")
        if tracker_id:
            try:
                issue_data["tracker_id"] = int(tracker_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid tracker_id '{tracker_id}', must be numeric")

        # status_id
        status_id = tool_parameters.get("status_id")
        if status_id:
            try:
                issue_data["status_id"] = int(status_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid status_id '{status_id}', must be numeric")

        # priority_id
        priority_id = tool_parameters.get("priority_id")
        if priority_id:
            try:
                issue_data["priority_id"] = int(priority_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid priority_id '{priority_id}', must be numeric")

        # subject (required)
        issue_data["subject"] = subject

        # description
        description = tool_parameters.get("description")
        if description:
            issue_data["description"] = description

        # category_id
        category_id = tool_parameters.get("category_id")
        if category_id:
            try:
                issue_data["category_id"] = int(category_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid category_id '{category_id}', must be numeric")

        # fixed_version_id
        fixed_version_id = tool_parameters.get("fixed_version_id")
        if fixed_version_id:
            try:
                issue_data["fixed_version_id"] = int(fixed_version_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid fixed_version_id '{fixed_version_id}', must be numeric")

        # assigned_to_id
        assigned_to_id = tool_parameters.get("assigned_to_id")
        if assigned_to_id:
            try:
                issue_data["assigned_to_id"] = int(assigned_to_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid assigned_to_id '{assigned_to_id}', must be numeric")

        # parent_issue_id
        parent_issue_id = tool_parameters.get("parent_issue_id")
        if parent_issue_id:
            try:
                issue_data["parent_issue_id"] = int(parent_issue_id)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid parent_issue_id '{parent_issue_id}', must be numeric")

        # custom_fields
        custom_fields = tool_parameters.get("custom_fields")
        if custom_fields:
            try:
                import json
                custom_fields_data = json.loads(custom_fields)
                if isinstance(custom_fields_data, list):
                    issue_data["custom_fields"] = custom_fields_data
                else:
                    yield self.create_text_message("Warning: custom_fields must be a JSON array")
            except json.JSONDecodeError:
                yield self.create_text_message("Warning: Invalid custom_fields JSON format")

        # watcher_user_ids
        watcher_user_ids = tool_parameters.get("watcher_user_ids")
        if watcher_user_ids:
            try:
                # Parse comma-separated string to array of integers
                watcher_ids = [int(uid.strip()) for uid in watcher_user_ids.split(",")]
                issue_data["watcher_user_ids"] = watcher_ids
            except ValueError:
                yield self.create_text_message("Warning: Invalid watcher_user_ids, must be comma-separated integers")

        # is_private
        is_private = tool_parameters.get("is_private")
        if is_private is not None:
            issue_data["is_private"] = bool(is_private)

        # estimated_hours
        estimated_hours = tool_parameters.get("estimated_hours")
        if estimated_hours:
            try:
                issue_data["estimated_hours"] = float(estimated_hours)
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid estimated_hours '{estimated_hours}', must be numeric")

        # Handle project_id conversion
        try:
            issue_data["project_id"] = int(project_id)
        except ValueError:
            # Keep as string if it's a project identifier
            pass

        # Prepare request payload
        payload = {
            "issue": issue_data
        }

        try:
            # Make API request
            response = requests.post(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 201:
                # Success - issue created
                data = response.json()
                result = data

                # Output success message and JSON data
                created_issue = data.get("issue", {})
                issue_id = created_issue.get("id")
                issue_subject = created_issue.get("subject")

                success_message = f"Issue created successfully: #{issue_id} - {issue_subject}"
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
                yield self.create_text_message("Error: Access denied. Check your API key permissions or project access")
                return

            elif response.status_code == 404:
                yield self.create_text_message("Error: Project not found. Check the project ID")
                return

            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error connecting to Redmine: {str(e)}")
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing Redmine response: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {str(e)}")
