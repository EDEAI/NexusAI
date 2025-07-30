from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class PingTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Debug information
        print("[DEBUG] Starting Ping operation")
        print(f"[DEBUG] Using API key: {api_key[:4]}...{api_key[-4:] if api_key else 'None'}")
        
        try:
            # Make request to ping endpoint
            url = "https://api.browser-use.com/api/v1/ping"
            print(f"[DEBUG] Sending request to {url}")
            
            # Ping endpoint doesn't require authentication, but we'll include it anyway
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Ping response status code: {response.status_code}")
            print(f"[DEBUG] Ping response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[DEBUG] Ping successful. Response parsed as JSON: {json.dumps(result, indent=2)}")
                except Exception as e:
                    result = response.text
                    print(f"[DEBUG] Ping successful. Response as text: {result}")
                
                # Return success message
                yield self.create_json_message({
                    "status": "success",
                    "message": "Browser Use API server is running and responding",
                    "response": result
                })
            else:
                error_message = f"Ping failed with status code: {response.status_code}"
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
            error_message = f"Unexpected error during ping operation: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
