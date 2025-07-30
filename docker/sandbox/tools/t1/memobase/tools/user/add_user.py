from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient

class AddUserTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        metadata_str = tool_parameters.get("metadata", "")

        metadata = {}
        if metadata_str:
            try:
                metadata = json.loads(metadata_str)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for metadata")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user_id = client.add_user(data=metadata)
            
            yield self.create_json_message({"status": "success", "user_id": user_id})
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })
