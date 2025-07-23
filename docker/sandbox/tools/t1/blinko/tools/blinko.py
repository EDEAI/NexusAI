from typing import Any, Dict, Optional
import json
import requests
from collections.abc import Generator
from datetime import datetime
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class BlinkoTool(Tool):
    @classmethod
    def from_credentials(cls, credentials: dict[str, Any]):
        """
        Create a tool instance from credentials
        
        Args:
            credentials: The credentials for the tool
            
        Returns:
            BlinkoTool instance
        """
        tool = cls()
        tool.runtime = type('obj', (object,), {
            'credentials': credentials
        })
        return tool
        
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke the tool with the parameters
        
        Args:
            tool_parameters: The parameters for the tool
            
        Yields:
            ToolInvokeMessage with the result
        """
        query = tool_parameters.get("query", "")
        result = self._execute(query)
        yield self.create_json_message(result)
        
    def _execute(self, query: str) -> Dict[str, Any]:
        """
        Execute the tool with the query
        
        Args:
            query: The content to save as a note
            
        Returns:
            Dict with success status and message
        """
        try:
            # Get credentials
            token = self.runtime.credentials.get('BLINKO_TOKEN', '')
            domain = self.runtime.credentials.get('BLINKO_DOMAIN', '')
            
            # Prepare request body
            request_body = {
                "0": {
                    "json": {
                        "content": query,
                        "type": 0,
                        "isArchived": None,
                        "isRecycle": None,
                        "id": None,
                        "attachments": [],
                        "isTop": None,
                        "isShare": None,
                        "references": [],
                        "createdAt": None,
                        "updatedAt": None,
                        "metadata": {}
                    },
                    "meta": {
                        "values": {
                            "isArchived": ["undefined"],
                            "isRecycle": ["undefined"],
                            "id": ["undefined"],
                            "isTop": ["undefined"],
                            "isShare": ["undefined"],
                            "createdAt": ["undefined"],
                            "updatedAt": ["undefined"]
                        }
                    }
                }
            }
            
            # Prepare headers
            headers = {
                "accept": "*/*",
                "content-type": "application/json",
                "authorization": f"Bearer {token}",
                "priority": "u=1, i",
                "sec-ch-ua": "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin"
            }
            
            # Make the request
            response = requests.post(
                f"{domain}/api/trpc/notes.upsert?batch=1",
                headers=headers,
                json=request_body,
                timeout=10
            )
            
            # Check response
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "success",
                    "note_content": query
                }
            else:
                return {
                    "success": False,
                    "message": f"save note failed: {response.status_code} - {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"save note failed: {str(e)}"
            }
