from collections.abc import Generator
from typing import Any, Dict, List
import json
import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RetrieveMem0Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        # Get API key from credentials
        api_key = self.runtime.credentials["mem0_api_key"]
        
        # Prepare payload for search
        payload = {
            "query": tool_parameters["query"],
            "user_id": tool_parameters["user_id"]
        }
        
        # Make direct HTTP request to mem0 API
        try:
            response = httpx.post(
                "https://api.mem0.ai/v1/memories/search/",
                json=payload,
                headers={"Authorization": f"Token {api_key}"},
                timeout=30
            )
            response.raise_for_status()
            results = response.json()
            
            # Return JSON format
            yield self.create_json_message({
                "query": tool_parameters["query"],
                "results": [{
                    "id": r["id"],
                    "memory": r["memory"],
                    "score": r["score"],
                    "categories": r.get("categories", []),
                    "created_at": r["created_at"]
                } for r in results]
            })
            
            # Return text format
            text_response = f"Query: {tool_parameters['query']}\n\nResults:\n"
            if results:
                for idx, r in enumerate(results, 1):
                    text_response += f"\n{idx}. Memory: {r['memory']}"
                    text_response += f"\n   Score: {r['score']:.2f}"
                    text_response += f"\n   Categories: {', '.join(r.get('categories', []))}"
            else:
                text_response += "\nNo results found."
                
            yield self.create_text_message(text_response)
            
        except httpx.HTTPStatusError as e:
            error_message = f"HTTP error: {e.response.status_code}"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    error_message = f"Error: {error_data['detail']}"
            except:
                pass
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to retrieve memory: {error_message}")
            
        except Exception as e:
            error_message = f"Error: {str(e)}"
            
            yield self.create_json_message({
                "status": "error",
                "error": error_message
            })
            
            yield self.create_text_message(f"Failed to retrieve memory: {error_message}")
