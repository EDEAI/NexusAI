import logging
from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class GetGroupMembersTool(Tool):
    """Get RongCloud group members tool class
    
    Used to get RongCloud group members, need to provide group ID.
    The tool will return group members.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call get group members interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.group_id: Group ID (required)
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "group/user/query.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Get group members failed: {str(e)}")

        
        
    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('group_id'):
            raise Exception("Missing required parameter: group_id")
        return {
            "groupId": tool_parameters['group_id']
        }