from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient, ChatBlob

class InsertDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        user_id = tool_parameters.get("user_id", "")
        user_message = tool_parameters.get("user_message", "")
        assistant_message = tool_parameters.get("assistant_message", "")

        if not user_id:
            raise ValueError("User ID is required")
        if not user_message:
            raise ValueError("User message is required")
        if not assistant_message:
            raise ValueError("Assistant message is required")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            chat_blob = ChatBlob(messages=[
                {
                    "role": "user",
                    "content": user_message
                },
                {
                    "role": "assistant",
                    "content": assistant_message
                }
            ])

            user = client.get_user(user_id=user_id)
            bid = user.insert(chat_blob)
            
            yield self.create_json_message({
                "status": "success",
                "user_id": user_id,
                "blob_id": bid,
                "message": "Data inserted successfully"
            })
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })