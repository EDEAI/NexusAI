import logging
from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class GetUserInfoTool(Tool):
    """Get RongCloud user info tool class
    
    Used to get RongCloud user info, need to provide user ID.
    The tool will return user info, which can be used for subsequent RongCloud API calls.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call get user info interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.user_id: User ID (required)
                
        Yields: 
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "user/info.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Get user info failed: {str(e)}")

        
        
    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('user_id'):
            raise Exception("Missing required parameter: user_id")
            
        return {
            "userId": tool_parameters['user_id']
        }