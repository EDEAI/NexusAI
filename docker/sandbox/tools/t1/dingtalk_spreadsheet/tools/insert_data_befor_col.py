from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl, find_sheet_id_by_name
import random
import string
from datetime import datetime


class InsertDataBeforRowTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        table_id = getTableIdFromUrl(str(tool_parameters.get("table_id")))
        sheet_id = str(tool_parameters.get("sheet_id", ''))
        if not sheet_id:
            sheet_name = str(tool_parameters.get("sheet_name", ''))
            if not sheet_name:
                yield self.create_text_message('sheet_id 或 sheet_name 必须填写其中一个')
                return
            # 使用工具函数查找sheet_id
            sheet_id = find_sheet_id_by_name(client, table_id, sheet_name)
        if not sheet_id:
            yield self.create_text_message('sheet_id is empty')
        start_col = str(tool_parameters.get("start_col", 'A'))
        col_count = int(tool_parameters.get("col_count", 0))
        start_row = int(tool_parameters.get("start_row", 0))
        if start_row <= 0:
            start_row = 0
        else:
            start_row -= 1
        # 获取values字符串
        values = []
        values_str = str(tool_parameters.get("values", '[[]]'))
        try:
            # 尝试直接解析JSON
            values = json.loads(values_str)
        except json.JSONDecodeError:
            try:
                # 如果JSON解析失败，尝试将Python列表字面量转换为JSON
                # 替换单引号为双引号
                values_str = values_str.replace("'", '"')
                values = json.loads(values_str)
            except:
                # 如果仍然失败，尝试使用eval安全解析(仅用于列表和基本类型)
                yield self.create_text_message('values is not a valid json')
        if col_count == 0:
            col_count = len(values[0])
        res = client.insert_column_before_column(table_id, sheet_id, start_col, col_count, start_row, values)
        yield self.create_json_message(res)
