from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class InsertRecordsAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        sheet_id_or_name = str(tool_parameters.get("sheet_id_or_name"))
        
        records_str = tool_parameters.get("records", "")
        if not records_str:
            yield self.create_text_message("记录数据不能为空")
            return
            
        try:
            records = json.loads(records_str)
        except json.JSONDecodeError:
            yield self.create_text_message("记录数据格式错误，请提供有效的JSON格式")
            return
            
        # 插入记录
        res = client.insert_records(base_id, sheet_id_or_name, records)
        yield self.create_json_message(res) 
 