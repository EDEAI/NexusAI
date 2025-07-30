from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RedmineUpdateIssueTool(Tool):
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

        # Build issue data following API documentation order
        issue_data = {}
        has_updates = False

        # project_id
        project_id = tool_parameters.get("project_id")
        if project_id:
            try:
                issue_data["project_id"] = int(project_id)
            except ValueError:
                issue_data["project_id"] = project_id  # Keep as string if it's a project identifier
            has_updates = True

        # tracker_id
        tracker_id = tool_parameters.get("tracker_id")
        if tracker_id:
            try:
                issue_data["tracker_id"] = int(tracker_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid tracker_id '{tracker_id}', must be numeric")

        # status_id
        status_id = tool_parameters.get("status_id")
        if status_id:
            try:
                issue_data["status_id"] = int(status_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid status_id '{status_id}', must be numeric")

        # priority_id
        priority_id = tool_parameters.get("priority_id")
        if priority_id:
            try:
                issue_data["priority_id"] = int(priority_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid priority_id '{priority_id}', must be numeric")

        # subject
        subject = tool_parameters.get("subject")
        if subject:
            issue_data["subject"] = subject
            has_updates = True

        # description
        description = tool_parameters.get("description")
        if description:
            issue_data["description"] = description
            has_updates = True

        # category_id
        category_id = tool_parameters.get("category_id")
        if category_id:
            try:
                issue_data["category_id"] = int(category_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid category_id '{category_id}', must be numeric")

        # fixed_version_id
        fixed_version_id = tool_parameters.get("fixed_version_id")
        if fixed_version_id:
            try:
                issue_data["fixed_version_id"] = int(fixed_version_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid fixed_version_id '{fixed_version_id}', must be numeric")

        # assigned_to_id
        assigned_to_id = tool_parameters.get("assigned_to_id")
        if assigned_to_id:
            try:
                issue_data["assigned_to_id"] = int(assigned_to_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid assigned_to_id '{assigned_to_id}', must be numeric")

        # parent_issue_id
        parent_issue_id = tool_parameters.get("parent_issue_id")
        if parent_issue_id:
            try:
                issue_data["parent_issue_id"] = int(parent_issue_id)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid parent_issue_id '{parent_issue_id}', must be numeric")

        # custom_fields
        custom_fields = tool_parameters.get("custom_fields")
        if custom_fields:
            try:
                custom_fields_data = json.loads(custom_fields)
                if isinstance(custom_fields_data, list):
                    issue_data["custom_fields"] = custom_fields_data
                    has_updates = True
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
                has_updates = True
            except ValueError:
                yield self.create_text_message("Warning: Invalid watcher_user_ids, must be comma-separated integers")

        # is_private
        is_private = tool_parameters.get("is_private")
        if is_private is not None:
            issue_data["is_private"] = bool(is_private)
            has_updates = True

        # estimated_hours
        estimated_hours = tool_parameters.get("estimated_hours")
        if estimated_hours:
            try:
                issue_data["estimated_hours"] = float(estimated_hours)
                has_updates = True
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid estimated_hours '{estimated_hours}', must be numeric")

        # notes
        notes = tool_parameters.get("notes")
        if notes:
            issue_data["notes"] = notes
            has_updates = True

        # private_notes
        private_notes = tool_parameters.get("private_notes")
        if private_notes is not None:
            issue_data["private_notes"] = bool(private_notes)
            has_updates = True

        # done_ratio
        done_ratio = tool_parameters.get("done_ratio")
        if done_ratio:
            try:
                done_ratio_int = int(done_ratio)
                if 0 <= done_ratio_int <= 100:
                    issue_data["done_ratio"] = done_ratio_int
                    has_updates = True
                else:
                    yield self.create_text_message(f"Warning: Invalid done_ratio '{done_ratio}', must be between 0 and 100")
            except ValueError:
                yield self.create_text_message(f"Warning: Invalid done_ratio '{done_ratio}', must be numeric")

        if not has_updates:
            yield self.create_text_message("Error: No parameters provided for update. At least one field must be specified.")
            return

        # Prepare request payload
        payload = {
            "issue": issue_data
        }

        try:
            # Make API request
            response = requests.put(api_url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                # Success - issue updated
                success_message = f"Issue #{issue_id} updated successfully"
                yield self.create_text_message(success_message)

                # Try to get the updated issue details
                try:
                    get_response = requests.get(api_url, headers=headers, timeout=30)
                    if get_response.status_code == 200:
                        updated_data = get_response.json()
                        yield self.create_json_message(updated_data)
                    else:
                        yield self.create_json_message({"message": f"Issue #{issue_id} updated successfully", "updated_fields": list(issue_data.keys())})
                except:
                    yield self.create_json_message({"message": f"Issue #{issue_id} updated successfully", "updated_fields": list(issue_data.keys())})

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
                yield self.create_text_message("Error: Access denied. Check your API key permissions or issue access")
                return

            elif response.status_code == 404:
                yield self.create_text_message(f"Error: Issue #{issue_id} not found")
                return

            else:
                response.raise_for_status()

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error connecting to Redmine: {str(e)}")
        except json.JSONDecodeError as e:
            yield self.create_text_message(f"Error parsing Redmine response: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"Unexpected error: {str(e)}")
