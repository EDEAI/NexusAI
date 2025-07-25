import logging
from collections.abc import Generator
import time
from typing import Any, Dict

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class GetPrivateMessagesTool(Tool):
    """Get private messages from RongCloud tool class
    
    Used to get private messages from RongCloud, need to provide message ID.
    The tool will return private messages, which can be used for subsequent RongCloud API calls.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call get private messages interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.target_id: Target user ID (required)
                - parameters.data_time: Data time (required)
                - parameters.size: Message size (required)
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "v3/message/private/query.json", data, is_json=True)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Get private messages failed: {str(e)}")

        
        
    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('user_id'):
            raise Exception("Missing required parameter: user_id")
            
        if not tool_parameters.get('target_id'):
            raise Exception("Missing required parameter: target_id")
            
        # if not tool_parameters.get('start_time'):
        #     raise Exception("Missing required parameter: start_time")
            
        # if not tool_parameters.get('end_time'):
        #     raise Exception("Missing required parameter: end_time")
            
        # if not tool_parameters.get('include_start_time'):
        #     raise Exception("Missing required parameter: include_start_time")
        
        request_data = {
            "userId": tool_parameters['user_id'],
            "targetId": tool_parameters['target_id'],
            # "startTime": tool_parameters['start_time'],
            # "endTime": tool_parameters['end_time'],
            # "includeStart": tool_parameters['include_start_time']
            } 
        # Get the current timestamp and set it as the start and end time
        current_time = int(time.time() * 1000)  
        request_data['startTime'] = current_time
        # The last day
        request_data['endTime'] = current_time - 1000 * 60 * 60 * 24
        # The page size is 100
        request_data['pageSize']=100
        # The include start time is false
        request_data['includeStart']=False
        
        # if 'page_size' in tool_parameters:
        #     request_data['pageSize'] = tool_parameters['page_size']
            
        return request_data