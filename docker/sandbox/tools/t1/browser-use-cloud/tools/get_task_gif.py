from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class GetTaskGifTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Get parameters
        task_id = tool_parameters.get('task_id')
        
        # Debug information
        print("[DEBUG] Starting Get Task GIF operation")
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
            # Make request to get task GIF
            url = f"https://api.browser-use.com/api/v1/task/{task_id}/gif"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Get Task GIF response status code: {response.status_code}")
            print(f"[DEBUG] Get Task GIF response content length: {len(response.text)} characters")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    gif_url = result.get("gif")
                    
                    if gif_url:
                        print(f"[DEBUG] Successfully retrieved GIF URL for task {task_id}")
                        
                        # Return success message with GIF URL
                        yield self.create_json_message({
                            "status": "success",
                            "message": f"Successfully retrieved GIF animation for task {task_id}.",
                            "gif_url": gif_url,
                            "task_id": task_id
                        })
                    else:
                        print(f"[DEBUG] No GIF available for task {task_id}")
                        yield self.create_json_message({
                            "status": "success",
                            "message": f"No GIF animation available for task {task_id}. This may be because the task is not yet complete or no screenshots were captured during execution.",
                            "gif_url": None,
                            "task_id": task_id
                        })
                except Exception as e:
                    error_message = f"Failed to parse task GIF response: {str(e)}"
                    print(f"[DEBUG] {error_message}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_message,
                        "raw_response": response.text[:1000]  # Limit response text to avoid excessive output
                    })
            else:
                error_message = f"Failed to get task GIF with status code: {response.status_code}"
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
            error_message = f"Unexpected error during get task GIF operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
