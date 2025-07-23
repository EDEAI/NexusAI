from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient

class AddProfileTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        user_id = tool_parameters.get("user_id", "")
        topic = tool_parameters.get("topic", "")
        sub_topic = tool_parameters.get("sub_topic", "")
        content = tool_parameters.get("content", "")

        if not user_id:
            raise ValueError("User ID is required")
        if not topic:
            raise ValueError("Topic is required")
        if not sub_topic:
            raise ValueError("Sub-topic is required")
        if not content:
            raise ValueError("Content is required")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user = client.get_user(user_id=user_id)
            
            profile_id = user.add_profile(content=content, topic=topic, sub_topic=sub_topic)
            
            yield self.create_json_message({
                "status": "success",
                "user_id": user_id,
                "topic": topic,
                "sub_topic": sub_topic,
                "content": content,
                "profile_id": profile_id
            })
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })