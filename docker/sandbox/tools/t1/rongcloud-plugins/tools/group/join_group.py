import logging
from collections.abc import Generator
from typing import Any, Dict
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class JoinGroupTool(Tool):
    """Join RongCloud group tool class
    
    Used to join RongCloud group, need to provide member IDs and group ID.
    The tool will return success or failed.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call join group interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.member_ids: Member IDs to join the group (required)
                - parameters.group_id: Group ID (required)
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "group/join.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Join group failed: {str(e)}")

        
        
    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('member_ids'):
            raise Exception("Missing required parameter: member_ids")
            
        if not tool_parameters.get('group_id'):
            raise Exception("Missing required parameter: group_id")
            
        return {
            "userId": tool_parameters['member_ids'],
            "groupId": tool_parameters['group_id'],
        }