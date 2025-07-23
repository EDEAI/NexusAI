from collections.abc import Generator
from typing import Any
import json
from pyairtable import Api
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.common import validate_parameters

class AirtableToolInsert(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        required_fields = ["baseId", "tableId", "record"]
        if not validate_parameters(self, tool_parameters, required_fields):
            return
        baseId = tool_parameters["baseId"]
        tableId = tool_parameters["tableId"]
        record = tool_parameters["record"]
        api = Api(self.runtime.credentials['airtable_token'])
        table = api.table(baseId, tableId)
        if isinstance(record, str):
            try:
                record = json.loads(record)
            except json.JSONDecodeError:
                yield self.create_text_message("The record is invalid JSON string")
        try:
            table.create(record)
            yield self.create_text_message("Success")
        except Exception as e:
            yield self.create_text_message(f"Error：{e}")
