from typing import Any, Generator
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl, find_sheet_id_by_name
import random
import string
from datetime import datetime


class DelColTool(Tool):
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
        if col_count <= 0:
            yield self.create_text_message('col_count must be greater than 0')
            return
        res = client.delete_columns(table_id, sheet_id, start_col, col_count)
        yield self.create_text_message(res.get('id', '删除失败'))
