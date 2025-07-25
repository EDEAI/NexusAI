import logging
from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class UpdateUserInfoTool(Tool):
    """Update RongCloud user info tool class
    
    Used to update RongCloud user info, need to provide user ID, name and portrait URI.
    The tool will return updated user info.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call update user info interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.user_id: User ID (required)
                - parameters.name: User name (optional)
                - parameters.portrait_uri: User portrait URI (optional)
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "user/refresh.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Update user failed: {str(e)}")

    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('user_id'):
            raise Exception("Missing required parameter: user_id")
            
        result =  {
            "userId": tool_parameters['user_id'],
        }
        if "name" in tool_parameters:
            result['name'] = tool_parameters['name']
            
        if "portrait_uri" in tool_parameters:
            result['portraitUri'] = tool_parameters['portrait_uri']
    
        return result