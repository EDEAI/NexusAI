from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest

class GetOperatorIdTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        client = DingTalkRequest(app_id, app_secret)
        user_id = str(tool_parameters.get("user_id", ''))
        # 如果用户id为空，尝试用手机号获取用户id
        if not user_id:
            mobile = str(tool_parameters.get("mobile", ''))
            if not mobile:
                raise ValueError("user_id and mobile are both empty")
            user_id = str(client.get_user_id_by_mobile(mobile)) or ''
        if not user_id:
            raise ValueError("user_id is empty")   
        res = client.get_user_info(user_id)
        yield self.create_text_message(res.get("result", {}).get("unionid", ''))