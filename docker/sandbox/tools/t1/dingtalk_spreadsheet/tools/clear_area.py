from typing import Any, Generator
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl, find_sheet_id_by_name
import random
import string
from datetime import datetime


class ClearAreaTool(Tool):
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
        res = client.clear_range_data(table_id, sheet_id, area)
        yield self.create_json_message(res)
