from typing import Any, Generator
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage, uuid
from dingtalk_api_utils import DingTalkRequest, getTableIdFromUrl, find_sheet_id_by_name
import random
import string
from datetime import datetime


class ReadTableTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = str(self.runtime.credentials.get("app_key"))
        app_secret = str(self.runtime.credentials.get("app_secret"))
        operator_id = str(tool_parameters.get("operator_id"))
        client = DingTalkRequest(app_id, app_secret, operator_id)
        table_id = getTableIdFromUrl(str(tool_parameters.get("table_id")))
        res = client.get_all_sheets(table_id)
        result = {"sheets": res.get("value", [])}
        yield self.create_json_message(result)
