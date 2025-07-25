from typing import Any, Generator
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl
import random
import string
from datetime import datetime


class CreateSpreadsheetTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        table_id = getTableIdFromUrl(str(tool_parameters.get("table_id")))
        title = str(tool_parameters.get("title", ''))
        if not title:
            # 生成当前时间字符串
            current_time = datetime.now().strftime('%Y%m%d%H')
            # 生成2位随机英文字母
            random_letters = ''.join(random.choices(string.ascii_letters, k=2))
            title = f'NewSheet{current_time}{random_letters}'
        res = client.create_sheet(table_id, title)
        yield self.create_text_message(res.get("id", ''))
