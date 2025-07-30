from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class DeleteRecordsAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        sheet_id_or_name = str(tool_parameters.get("sheet_id_or_name"))
        
        record_ids_str = tool_parameters.get("record_ids", "")
        if not record_ids_str:
            yield self.create_text_message("记录ID不能为空")
            return
            
        try:
            record_ids = json.loads(record_ids_str)
        except json.JSONDecodeError:
            yield self.create_text_message("记录ID格式错误，请提供有效的JSON数组格式")
            return
            
        # 删除记录
        res = client.delete_records(base_id, sheet_id_or_name, record_ids)
        yield self.create_json_message(res) 