from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient

class UpdateEventTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        user_id = tool_parameters.get("user_id", "")
        event_id = tool_parameters.get("event_id", "")
        event_data_str = tool_parameters.get("event_data_str", "")

        if not user_id:
            raise ValueError("User ID is required")
        if not event_id:
            raise ValueError("Event ID is required")
        if not event_data_str:
            raise ValueError("Event data is required")
            
        try:
            event_data = json.loads(event_data_str)

            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user = client.get_user(user_id=user_id)
            
            result = user.update_event(
                event_id=event_id,
                event_data=event_data
            )
            
            yield self.create_json_message({
                "status": "success",
                "user_id": user_id,
                "event_id": event_id,
                "result": result
            })
            
        except json.JSONDecodeError as e:
            yield self.create_json_message({
                "status": "error",
                "message": f"Invalid JSON format for event_data: {str(e)}"
            })
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })