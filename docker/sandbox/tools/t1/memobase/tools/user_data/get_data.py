from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from memobase import MemoBaseClient
from memobase.core.blob import BlobType


class GetDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        user_id = tool_parameters.get("user_id", "")
        blob_id = tool_parameters.get("blob_id", "")
        page = tool_parameters.get("page", 1)
        page_size = tool_parameters.get("page_size", 10)

        if not user_id:
            raise ValueError("User ID is required")

        try:
            credentials = self.runtime.credentials
            memobase_url = credentials.get("memobase_url", "")
            memobase_api_key = credentials.get("memobase_api_key", "")
            
            client = MemoBaseClient(
                project_url=memobase_url,
                api_key=memobase_api_key,
            )
            
            user = client.get_user(user_id=user_id)
            
            if blob_id:
                data = user.get(blob_id=blob_id)
                result = {
                    "status": "success",
                    "data": data
                }
            else:
                blobs = user.get_all(blob_type=BlobType.chat, page=page-1, page_size=page_size)

                result = {
                    "status": "success",
                    "blob_count": len(blobs),
                    "blobs": blobs,
                    "page": page,
                    "page_size": page_size
                }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })