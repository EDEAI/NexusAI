from collections.abc import Generator
from typing import Any
import json
from pyairtable import Api
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.common import validate_parameters,validate_field_or_sort_parameters

class AirtableToolAll(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        required_fields = ["baseId", "tableId","pageSize","maxRecords"]
        if not validate_parameters(self, tool_parameters, required_fields):
            return
        baseId = tool_parameters["baseId"]
        tableId = tool_parameters["tableId"]
        api = Api(self.runtime.credentials['airtable_token'])
        table = api.table(baseId, tableId)
        schema = table.schema()
        fields = [field.name for field in schema.fields]   
        kwargs = {'page_size': tool_parameters["pageSize"],'max_records': tool_parameters["maxRecords"]}
        if tool_parameters.get("sort"):
            validation_result = list(validate_field_or_sort_parameters(self, tool_parameters["sort"], fields, 'sort'))
            if not validation_result:
                kwargs["sort"] = tool_parameters["sort"].strip().split(",")
            else:
                for message in validation_result:
                    yield message
                return
            
        if tool_parameters.get("fields"):
            validation_result = list(validate_field_or_sort_parameters(self, tool_parameters["fields"], fields,'fields'))
            if not validation_result:
                kwargs["fields"] = tool_parameters["fields"].strip().split(",")
            else:
                for message in validation_result:
                    yield message
                return
        if tool_parameters.get("filterByFormula"):
            kwargs["formula"] = tool_parameters["filterByFormula"].strip()
        try:
            records = table.all(**kwargs)
            if len(records) == 0:
                yield self.create_text_message("No records found")
                return
            else:
                '''
                返回的数据是 [ {
                    'id': 'rec123',
                    'fields': {
                        'Name': 'John',
                        'Age': 30,
                        'Email': 'EMAIL'
                    }
                    'id': 'rec123',
                    'fields': {
                        'Name': 'John',
                        'Age': 30,
                        'Email': 'EMAIL'
                    }
                ]
                需要处理为 [
                    {'id':'rec123','Name': 'John','Age': 30,'Email': 'EMAIL'},
                    {'id':'rec123','Name': 'John','Age': 30,'Email': 'EMAIL'}
                ]
                '''
                processed_records = []
                for record in records:
                    processed_record = {'id': record['id']}
                    processed_record.update(record['fields'])
                    processed_records.append(processed_record)
                result = json.dumps(processed_records, default=str)
                yield self.create_text_message(result)
        except Exception as e:
            yield self.create_text_message(f"Error：{e}")
