from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ListTasksTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        page = tool_parameters.get('page', 1)
        limit = tool_parameters.get('limit', 10)
        
        # Debug information
        print("[DEBUG] Starting List Tasks operation")
        print(f"[DEBUG] Using API key: {api_key[:4]}...{api_key[-4:] if api_key else 'None'}")
        print(f"[DEBUG] Page: {page}, Limit: {limit}")
        
        # Validate parameters
        if not api_key:
            error_message = "API key is required for this operation"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
        
        # Ensure page and limit are integers and have valid values
        try:
            page = int(page)
            if page < 1:
                page = 1
                print(f"[DEBUG] Invalid page value, using default: {page}")
        except (TypeError, ValueError):
            page = 1
            print(f"[DEBUG] Invalid page value, using default: {page}")
            
        try:
            limit = int(limit)
            if limit < 1:
                limit = 10
                print(f"[DEBUG] Invalid limit value, using default: {limit}")
        except (TypeError, ValueError):
            limit = 10
            print(f"[DEBUG] Invalid limit value, using default: {limit}")
        
        try:
            # Make request to list tasks
            url = "https://api.browser-use.com/api/v1/tasks"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            params = {
                "page": page,
                "limit": limit
            }
            
            print(f"[DEBUG] Sending request to {url} with params: {params}")
            response = requests.get(url, headers=headers, params=params)
            
            # Debug response information
            print(f"[DEBUG] List Tasks response status code: {response.status_code}")
            print(f"[DEBUG] List Tasks response content length: {len(response.text)} characters")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    tasks = result.get("tasks", [])
                    total_pages = result.get("total_pages", 0)
                    current_page = result.get("page", page)
                    total_count = result.get("total_count", 0)
                    
                    print(f"[DEBUG] Tasks retrieved successfully. Found {len(tasks)} tasks on page {current_page} of {total_pages}. Total tasks: {total_count}")
                    
                    # Create a summary of tasks
                    task_summaries = []
                    for task in tasks:
                        task_id = task.get("id")
                        task_description = task.get("task", "")
                        if len(task_description) > 50:
                            task_description = task_description[:47] + "..."
                        task_status = task.get("status")
                        task_created = task.get("created_at")
                        
                        task_summary = {
                            "id": task_id,
                            "description": task_description,
                            "status": task_status,
                            "created_at": task_created
                        }
                        task_summaries.append(task_summary)
                    
                    # Create pagination info
                    pagination = {
                        "current_page": current_page,
                        "total_pages": total_pages,
                        "total_tasks": total_count,
                        "tasks_per_page": limit
                    }
                    
                    # Create a human-readable message
                    if total_count == 0:
                        message = "No tasks found."
                    else:
                        message = f"Found {total_count} tasks. Showing page {current_page} of {total_pages} ({len(tasks)} tasks per page)."
                    
                    # Return success message with task list
                    yield self.create_json_message({
                        "status": "success",
                        "message": message,
                        "tasks": task_summaries,
                        "pagination": pagination,
                        "full_response": result  # Include the full response for advanced use cases
                    })
                except Exception as e:
                    print(f"[DEBUG] Could not parse response as JSON: Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse task list response: {str(e)}",
                        "raw_response": response.text[:1000]  # Limit response text to avoid excessive output
                    })
            else:
                error_message = f"Failed to list tasks with status code: {response.status_code}"
                print(f"[DEBUG] {error_message}")
                
                try:
                    error_data = response.json()
                    print(f"[DEBUG] Error response: {json.dumps(error_data, indent=2)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_message,
                        "error": error_data
                    })
                except Exception:
                    print(f"[DEBUG] Could not parse error response as JSON: {response.text[:500]}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_message,
                        "error": response.text[:1000]  # Limit response text to avoid excessive output
                    })
                
        except requests.RequestException as e:
            error_message = f"Failed to connect to Browser Use API: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
        except Exception as e:
            error_message = f"Unexpected error during list tasks operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
