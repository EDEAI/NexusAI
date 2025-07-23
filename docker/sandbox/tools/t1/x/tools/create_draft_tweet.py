import os
import json
from collections.abc import Generator
from typing import Any
from datetime import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class CreateDraftTweetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Extract content from parameters
        content = tool_parameters.get("content")
        
        if not content:
            yield self.create_error_message("Tweet content is required")
            return
        
        if len(content) > 280:
            yield self.create_error_message("Tweet content must be 280 characters or less")
            return
        
        try:
            # Create the draft tweet data
            draft = {
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            
            # Ensure drafts directory exists
            os.makedirs("drafts", exist_ok=True)
            
            # Save the draft to a file
            draft_id = f"draft_{int(datetime.now().timestamp())}.json"
            with open(os.path.join("drafts", draft_id), "w") as f:
                json.dump(draft, f, indent=2)
            
            # Return success message
            yield self.create_json_message({
                "status": "success",
                "draft_id": draft_id,
                "message": f"Draft tweet created with ID: {draft_id}"
            })
            
        except Exception as e:
            yield self.create_error_message(f"Error creating draft tweet: {str(e)}")