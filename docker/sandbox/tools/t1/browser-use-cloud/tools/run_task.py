from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RunTaskTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task = tool_parameters.get('task')
        save_browser_data = tool_parameters.get('save_browser_data', False)
        
        # Debug information
        print("[DEBUG] Starting Run Task operation")
        print(f"[DEBUG] Using API key: {api_key[:4]}...{api_key[-4:] if api_key else 'None'}")
        print(f"[DEBUG] Task description: {task}")
        print(f"[DEBUG] Save browser data: {save_browser_data}")
        
        # Validate parameters
        if not api_key:
            error_message = "API key is required for this operation"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
            
        if not task:
            error_message = "Task description is required"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
        
        try:
            # Prepare request data
            url = "https://api.browser-use.com/api/v1/run-task"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "task": task,
                "save_browser_data": save_browser_data
            }
            
            print(f"[DEBUG] Sending request to {url}")
            print(f"[DEBUG] Request data: {json.dumps(data, indent=2)}")
            
            # Make request
            response = requests.post(url, headers=headers, json=data)
            
            # Debug response information
            print(f"[DEBUG] Run Task response status code: {response.status_code}")
            print(f"[DEBUG] Run Task response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    task_id = result.get('id')
                    
                    if not task_id:
                        print("[DEBUG] Task ID not found in response")
                        yield self.create_json_message({
                            "status": "error",
                            "message": "Task ID not found in response",
                            "response": result
                        })
                        return
                    
                    print(f"[DEBUG] Task created successfully. Task ID: {task_id}")
                    
                    # Create response data with original JSON structure
                    response_data = {
                        "status": "success",
                        "message": f"Task created successfully. Task ID: {task_id}",
                        "task_id": task_id
                    }
                    
                    # Create a text message with just the task ID
                    yield self.create_text_message(task_id)
                    
                    # Return the JSON response with full details
                    yield self.create_json_message(response_data)
                except Exception as e:
                    print(f"[DEBUG] Could not parse response as JSON: {response.text}, Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse response: {str(e)}",
                        "raw_response": response.text
                    })
            else:
                error_message = f"Task creation failed with status code: {response.status_code}"
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
            error_message = f"Unexpected error during task creation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
