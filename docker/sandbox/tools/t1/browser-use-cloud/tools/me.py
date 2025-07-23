from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class MeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Debug information
        print("[DEBUG] Starting Me operation to verify API key")
        print(f"[DEBUG] Using API key: {api_key[:4]}...{api_key[-4:] if api_key else 'None'}")
        
        if not api_key:
            error_message = "API key is required for this operation"
            print(f"[DEBUG] Error: {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
            return
        
        try:
            # Make request to me endpoint
            url = "https://api.browser-use.com/api/v1/me"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Me response status code: {response.status_code}")
            print(f"[DEBUG] Me response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[DEBUG] API key validation successful. Response: {result}")
                    
                    # Return success message
                    yield self.create_json_message({
                        "status": "success",
                        "message": "API key is valid and authenticated",
                        "is_valid": result
                    })
                except Exception as e:
                    print(f"[DEBUG] Could not parse response as JSON: {response.text}, Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse response: {str(e)}",
                        "raw_response": response.text
                    })
            else:
                error_message = f"API key validation failed with status code: {response.status_code}"
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
            error_message = f"Unexpected error during API key validation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
