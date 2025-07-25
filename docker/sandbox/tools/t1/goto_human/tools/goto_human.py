from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import json


class GotohumanTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            yield self.create_text_message("Error: GOTO_HUMAN_API_KEY not set")
            return
        

        try:
            response = requests.post(
                "https://api.gotohuman.com/requestReview",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "formId": tool_parameters["form_id"],
                    "fields": {k: v.replace('\\n', '\n').replace('\\', '') if isinstance(v, str) else v 
                              for k, v in json.loads(tool_parameters["content"]).items()},
                    "meta": tool_parameters.get("metadata", {}),
                }
            )
            response.raise_for_status()
            result = response.json()
            
            yield self.create_json_message({
                "review_id": result.get("reviewId", "N/A"),
                "status": "pending"
            })
            
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")