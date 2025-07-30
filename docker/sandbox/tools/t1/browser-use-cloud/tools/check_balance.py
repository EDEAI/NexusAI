from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class CheckBalanceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get API key from credentials
        api_key = self.runtime.credentials.get('browser_use_api_key')
        
        # Debug information
        print("[DEBUG] Starting Check Balance operation")
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
            # Make request to balance endpoint
            url = "https://api.browser-use.com/api/v1/balance"
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            print(f"[DEBUG] Sending request to {url}")
            response = requests.get(url, headers=headers)
            
            # Debug response information
            print(f"[DEBUG] Balance response status code: {response.status_code}")
            print(f"[DEBUG] Balance response content: {response.text}")
            
            # Process response
            if response.status_code == 200:
                try:
                    result = response.json()
                    balance = result.get('balance', 0)
                    print(f"[DEBUG] Balance check successful. Current balance: {balance} credits")
                    
                    # Format balance for display (1 credit = $0.01 USD)
                    usd_balance = balance / 100.0
                    
                    # Create a text message with just the balance value
                    yield self.create_text_message(str(balance))
                    
                    # Return the JSON response with full details
                    yield self.create_json_message({
                        "status": "success",
                        "message": f"Your current balance is {balance} credits (${usd_balance:.2f} USD)",
                        "balance": balance,
                        "balance_usd": usd_balance
                    })
                except Exception as e:
                    print(f"[DEBUG] Could not parse response as JSON: {response.text}, Error: {str(e)}")
                    yield self.create_json_message({
                        "status": "error",
                        "message": f"Could not parse balance response: {str(e)}",
                        "raw_response": response.text
                    })
            else:
                error_message = f"Balance check failed with status code: {response.status_code}"
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
            error_message = f"Unexpected error during balance check: {str(e)}"
            print(f"[DEBUG] {error_message}")
            yield self.create_json_message({
                "status": "error",
                "message": error_message
            })
