from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class CreateSheetAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        name = str(tool_parameters.get("name"))
        
        fields_str = tool_parameters.get("fields", "")
        fields = None
        if fields_str:
            try:
                fields = json.loads(fields_str)
            except json.JSONDecodeError:
                yield self.create_text_message("字段定义格式错误，请提供有效的JSON格式")
                return
        
        # 创建数据表
        res = client.create_sheet(base_id, name, fields)
        yield self.create_json_message(res) 