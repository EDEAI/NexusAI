import logging
from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class DismissGroupTool(Tool):
    """Dismiss RongCloud group tool class
    
    Used to dismiss RongCloud group, need to provide operator's user ID and group ID.
    The tool will return success or failed.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call dismiss group interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.user_id: User ID (required)
                - parameters.group_id: Group ID (required)
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "group/dismiss.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Dismiss group failed: {str(e)}")

        
        
    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('user_id'):
            raise Exception("Missing required parameter: user_id")
            
        if not tool_parameters.get('group_id'):
            raise Exception("Missing required parameter: group_id")
            
        return {
            "userId": tool_parameters['user_id'],
            "groupId": tool_parameters['group_id']
        }