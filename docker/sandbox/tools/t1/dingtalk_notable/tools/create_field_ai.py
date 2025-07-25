from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class CreateFieldAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        sheet_id_or_name = str(tool_parameters.get("sheet_id_or_name"))
        name = str(tool_parameters.get("name"))
        field_type = str(tool_parameters.get("type"))
        
        property_str = tool_parameters.get("property", "")
        property_dict = None
        if property_str:
            try:
                property_dict = json.loads(property_str)
            except json.JSONDecodeError:
                yield self.create_text_message("字段属性格式错误，请提供有效的JSON格式")
                return
        
        # 创建字段
        res = client.create_field(base_id, sheet_id_or_name, name, field_type, property_dict)
        yield self.create_json_message(res) 