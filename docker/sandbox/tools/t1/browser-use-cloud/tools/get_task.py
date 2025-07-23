from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task_id = tool_parameters.get('task_id')
        
        # Debug information
        print("[DEBUG] Starting Get Task Details operation")
        print(f"[DEBUG] Using API key: {api_key[:4]}...{api_key[-4:] if api_key else 'None'}")
        print(f"[DEBUG] Task ID: {task_id}")
        
        # Validate parameters
        if not api_key:
            error_message = "API key is required for this operation"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
            
        if not task_id:
            error_message = "Task ID is required"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
        
        try:
            # Make request to get task details
            url = f"https://api.browser-use.com/api/v1/task/{task_id}"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Get Task Details response status code: {response.status_code}")
            print(f"[DEBUG] Get Task Details response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[DEBUG] Task details retrieved successfully")
                    
                    # Extract key information
                    task_info = {
                        "id": result.get("id"),
                        "task": result.get("task"),
                        "status": result.get("status"),
                        "created_at": result.get("created_at"),
                        "finished_at": result.get("finished_at"),
                        "live_url": result.get("live_url"),
                        "output": result.get("output"),
                        "steps_count": len(result.get("steps", [])),
                        "has_browser_data": bool(result.get("browser_data"))
                    }
                    
                    # Create a human-readable status message
                    status = task_info.get("status")
                    status_messages = {
                        "created": "Task has been created but not yet started",
                        "running": "Task is currently running",
                        "finished": "Task has completed successfully",
                        "stopped": "Task was manually stopped",
                        "paused": "Task execution is temporarily paused",
                        "failed": "Task encountered an error and could not complete"
                    }
                    
                    status_message = status_messages.get(status, f"Unknown status: {status}")
                    
                    # Create a summary message
                    summary = f"Task '{task_info['task']}' is {status_message}"
                    if task_info.get("finished_at"):
                        summary += f" (completed at {task_info['finished_at']})"
                    if task_info.get("live_url"):
                        summary += f". A live preview URL is available."
                    if task_info.get("output"):
                        summary += f" Task output: {task_info['output']}"
                    
                    # If output is not None, add text field with the output result
                    if task_info.get("output"):
                        print(f"[DEBUG] Task has output, creating text message with output")
                        # Create a text message with the output
                        yield self.create_text_message(task_info.get("output"))
                        
                        # Create a clean JSON response without duplicate content
                        response_data = {
                            "status": "success",
                            "message": f"Task completed successfully. Task ID: {task_info['id']}",
                            "task_details": {
                                "id": task_info['id'],
                                "created_at": task_info['created_at'],
                                "finished_at": task_info['finished_at'],
                                "status": task_info['status'],
                                "live_url": task_info.get('live_url'),
                                "has_browser_data": bool(task_info.get('browser_data')),
                                "steps_count": len(task_info.get('steps', []))
                            },
                            "full_response": result
                        }
                        
                        # Return the JSON response
                        yield self.create_json_message(response_data)
                    else:
                        # For tasks without output, return just the JSON response as before
                        yield self.create_json_message({
                            "status": "success",
                            "message": f"Task completed successfully. Task ID: {task_info['id']}",
                            "task_details": {
                                "id": task_info['id'],
                                "created_at": task_info['created_at'],
                                "finished_at": task_info['finished_at'],
                                "status": task_info['status'],
                                "live_url": task_info.get('live_url'),
                                "has_browser_data": bool(task_info.get('browser_data')),
                                "steps_count": len(task_info.get('steps', []))
                            },
                            "full_response": result
                        })
                except Exception as e:
                    print(f"[DEBUG] Could not parse response as JSON: {response.text}, Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse task details response: {str(e)}",
                        "raw_response": response.text
                    })
            else:
                error_message = f"Failed to get task details with status code: {response.status_code}"
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
                    print(f"[DEBUG] Could not parse error response as JSON: {response.text}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_message,
                        "error": response.text
                    })
                
        except requests.RequestException as e:
            error_message = f"Failed to connect to Browser Use API: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
        except Exception as e:
            error_message = f"Unexpected error during get task details operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
