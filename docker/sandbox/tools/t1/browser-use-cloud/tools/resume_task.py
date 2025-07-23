from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ResumeTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task_id = tool_parameters.get('task_id')
        
        # Debug information
        print("[DEBUG] Starting Resume Task operation")
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
            # Make request to resume task
            url = f"https://api.browser-use.com/api/v1/resume-task"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            params = {
                "task_id": task_id
            }
            
            print(f"[DEBUG] Sending request to {url} with params: {params}")
            response = requests.put(url, headers=headers, params=params)
            
            # Debug response information
            print(f"[DEBUG] Resume Task response status code: {response.status_code}")
            print(f"[DEBUG] Resume Task response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                print(f"[DEBUG] Task resumed successfully")
                
                # Return success message
                yield self.create_json_message({
                    "status": "success",
                    "message": f"Task {task_id} has been successfully resumed and is now running.",
                    "task_id": task_id
                })
            else:
                error_message = f"Failed to resume task with status code: {response.status_code}"
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
            error_message = f"Unexpected error during resume task operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
