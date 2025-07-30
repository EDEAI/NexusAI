from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dingtalk_api_utils import DingTalkRequest


class ListRecordsAITool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        base_id = str(tool_parameters.get("base_id"))
        sheet_id_or_name = str(tool_parameters.get("sheet_id_or_name"))
        max_results = int(tool_parameters.get("max_results", 100))
        if max_results > 100:
            max_results = 100
        if max_results < 1:
            max_results = 1
        next_token = tool_parameters.get("next_token", None)
        
        filter_str = tool_parameters.get("filter", "")
        if filter_str:
            try:
                filter = json.loads(filter_str)
            except json.JSONDecodeError:
                yield self.create_text_message("筛选条件格式错误，请提供有效的JSON格式")
                return
        else:
            filter = None
        
        # 获取记录列表
        res = client.list_records(base_id, sheet_id_or_name, max_results, next_token, filter)
        yield self.create_json_message(res) 