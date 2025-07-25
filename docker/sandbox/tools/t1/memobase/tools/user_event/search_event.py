from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient

class SearchEventTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        user_id = tool_parameters.get("user_id", "")
        query = tool_parameters.get("query", "")
        topk = tool_parameters.get("topk", 10)
        similarity_threshold = tool_parameters.get("similarity_threshold", 0.5)
        time_range_in_days = tool_parameters.get("time_range_in_days", 7)

        if not user_id:
            raise ValueError("User ID is required")
        if not query:
            raise ValueError("Search query is required")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user = client.get_user(user_id=user_id)
            
            events = user.search_event(
                query=query,
                topk=topk,
                similarity_threshold=similarity_threshold,
                time_range_in_days=time_range_in_days
            )
            
            yield self.create_json_message({
                "status": "success",
                "user_id": user_id,
                "query": query,
                "topk": topk,
                "similarity_threshold": similarity_threshold,
                "time_range_in_days": time_range_in_days,
                "events": [event.model_dump() for event in events]
            })
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })