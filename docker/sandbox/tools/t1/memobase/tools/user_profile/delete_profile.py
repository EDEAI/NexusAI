from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient

class DeleteProfileTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        user_id = tool_parameters.get("user_id", "")
        profile_id = tool_parameters.get("profile_id", "")

        if not user_id:
            raise ValueError("User ID is required")
        if not profile_id:
            raise ValueError("Profile ID is required")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user = client.get_user(user_id=user_id)
            
            result = user.delete_profile(profile_id=profile_id)
            
            yield self.create_json_message({
                "status": "success",
                "user_id": user_id,
                "profile_id": profile_id,
                "result": result
            })
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })