from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class GetAllFieldsAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        sheet_id_or_name = str(tool_parameters.get("sheet_id_or_name"))
        
        # 获取所有字段
        res = client.get_all_fields(base_id, sheet_id_or_name)
        yield self.create_json_message(res) 