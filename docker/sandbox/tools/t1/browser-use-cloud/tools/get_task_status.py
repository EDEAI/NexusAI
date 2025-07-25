from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetTaskStatusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task_id = tool_parameters.get('task_id')
        
        # Debug information
        print("[DEBUG] Starting Get Task Status operation")
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
            # Make request to get task status
            url = f"https://api.browser-use.com/api/v1/task/{task_id}/status"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Get Task Status response status code: {response.status_code}")
            print(f"[DEBUG] Get Task Status response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    # The response is a simple string, not a JSON object
                    status = response.text.strip().replace('"', '')
                    print(f"[DEBUG] Task status retrieved successfully: {status}")
                    
                    # Create a human-readable status message
                    status_messages = {
                        "created": "Task has been created but not yet started",
                        "running": "Task is currently running",
                        "finished": "Task has completed successfully",
                        "stopped": "Task was manually stopped",
                        "paused": "Task execution is temporarily paused",
                        "failed": "Task encountered an error and could not complete"
                    }
                    
                    status_message = status_messages.get(status, f"Unknown status: {status}")
                    
                    # Create a text message with just the task status
                    yield self.create_text_message(status)
                    
                    # Return success message with task status
                    yield self.create_json_message({
                        "status": "success",
                        "message": f"Task status: {status_message}",
                        "task_status": status
                    })
                except Exception as e:
                    print(f"[DEBUG] Could not parse response: {response.text}, Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse task status response: {str(e)}",
                        "raw_response": response.text
                    })
            else:
                error_message = f"Failed to get task status with status code: {response.status_code}"
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
            error_message = f"Unexpected error during get task status operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
