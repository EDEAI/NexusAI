from typing import Any, Generator
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl, find_sheet_id_by_name
import random
import string
from datetime import datetime


class UpdateAreaTool(Tool):
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
        area = str(tool_parameters.get("area", ''))
        if not area:
            yield self.create_text_message('cells is empty')
        # 解析区域
        area = area.upper()
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
        res = client.update_range_data(table_id, sheet_id, area, values)
        yield self.create_text_message(res.get("a1Notation", '更新失败'))
