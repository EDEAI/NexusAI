import json
import logging
from collections.abc import Generator
from typing import Any, Dict

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.rongcloud import RongCloudAPI

logger = logging.getLogger(__name__)

class SendGroupTextMessageTool(Tool):
    """Send RongCloud group text message tool class
    
    Used to send RongCloud group text message, support setting sender, receiver and message content.
    The tool will return the result of message sending, including message ID, etc.
    """
    
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Call send message interface
        
        Args:
            tool_parameters: Tool parameters, including:
                - parameters.from_user_id: Sender user ID
                - parameters.to_group_id: Recipient group IDs, separated by commas, for example "123,456,789"
                - parameters.content: Message content
                
        Yields:
            ToolInvokeMessage: Tool call message with execution result
        """
        try:
            rongcloud_api = RongCloudAPI(self.runtime)
            data = self.get_request_data(tool_parameters)
            result = rongcloud_api._make_request("POST", "message/group/publish.json", data)
            yield self.create_json_message(result.json())
        except Exception as e:
            raise Exception(f"Send message failed: {str(e)}")


    def get_request_data(self, tool_parameters: Dict[str, Any]) -> Dict[str, Any]:
        if not tool_parameters.get('from_user_id'):
            raise Exception("Missing required parameter: from_user_id")
            
        if not tool_parameters.get('to_group_id'):
            raise Exception("Missing required parameter: to_group_id")
            
        if not tool_parameters.get('content'):
            raise Exception("Missing required parameter: content")
        
        # if not tool_parameters.get('object_name'):
        #     raise Exception("Missing required parameter: object_name")

        request_data = {
            "fromUserId": tool_parameters['from_user_id'],
            "toGroupId": tool_parameters['to_group_id'],
            "objectName": "RC:TxtMsg",
            "isIncludeSender": 1,
            "content": json.dumps({"content": tool_parameters['content']}, ensure_ascii=False)
        }

        # if "is_mentioned" in tool_parameters:
        #     request_data['isMentioned'] = tool_parameters['is_mentioned']
        # if "push_content" in tool_parameters:
        #     request_data['pushContent'] = tool_parameters['push_content']
        # if "push_data" in tool_parameters:
        #     request_data['pushData'] = tool_parameters['push_data']
        # if "is_include_sender" in tool_parameters:
        #     request_data['isIncludeSender'] = tool_parameters['is_include_sender']
        # if 'is_persisted' in tool_parameters:
        #     request_data['isPersisted'] = tool_parameters['is_persisted']
        # if "content_available" in tool_parameters:
        #     request_data['contentAvailable'] = tool_parameters['content_available']
        # if "expansion" in tool_parameters:
        #     request_data['expansion'] = tool_parameters['expansion']
        # if "extra_content" in tool_parameters:
        #     request_data['extraContent'] = tool_parameters['extra_content']
        # if "disable_push" in tool_parameters:
        #     request_data['disablePush'] = tool_parameters['disable_push']
        # if "push_ext" in tool_parameters:
        #     request_data['pushExt'] = tool_parameters['push_ext']
        # if "disable_update_last_msg" in tool_parameters:
        #     request_data['disableUpdateLastMsg'] = tool_parameters['disable_update_last_msg']
        # if "need_read_receipt" in tool_parameters:
        #     request_data['needReadReceipt'] = tool_parameters['need_read_receipt']

        return request_data