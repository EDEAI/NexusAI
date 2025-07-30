from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetTaskMediaTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task_id = tool_parameters.get('task_id')
        
        # Debug information
        print("[DEBUG] Starting Get Task Media operation")
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
            # Make request to get task media
            url = f"https://api.browser-use.com/api/v1/task/{task_id}/media"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Get Task Media response status code: {response.status_code}")
            print(f"[DEBUG] Get Task Media response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    recordings = result.get("recordings", [])
                    
                    if recordings and len(recordings) > 0:
                        print(f"[DEBUG] Found {len(recordings)} recordings for task {task_id}")
                        
                        # If recordings exist, create a text message with the URL
                        if recordings:
                            print(f"[DEBUG] Found recordings, creating text message with URL")
                            yield self.create_text_message(recordings[0])  # Output the first recording URL
                        
                        # Return the JSON response with full details
                        yield self.create_json_message({
                            "status": "success",
                            "message": f"Successfully retrieved {len(recordings)} media recordings for task {task_id}.",
                            "recordings": recordings,
                            "task_id": task_id
                        })
                    else:
                        print(f"[DEBUG] No recordings found for task {task_id}")
                        yield self.create_json_message({
                            "status": "success",
                            "message": f"No media recordings found for task {task_id}. This may be because the task is not yet complete or no recordings were generated.",
                            "recordings": [],
                            "task_id": task_id
                        })
                except Exception as e:
                    error_message = f"Failed to parse task media response: {str(e)}"
                    print(f"[DEBUG] {error_message}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_message,
                        "raw_response": response.text
                    })
            else:
                error_message = f"Failed to get task media with status code: {response.status_code}"
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
            error_message = f"Unexpected error during get task media operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
