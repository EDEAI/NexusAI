from typing import Any, Generator, Optional
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


def validate_parameters(tool: Tool, params: dict[str, Any], required_fields: list[str]) -> Generator[Optional[ToolInvokeMessage], None, bool]:
    for field in required_fields:
        if not params.get(field):
            yield tool.create_text_message(f"Please provide {field}")
            return False
    return True

def validate_field_or_sort_parameters(tool: Tool, inputs:str, fields:list[str],validate_type:str) -> Generator[Optional[ToolInvokeMessage], None, bool]:
    input_fields_list = inputs.split(",")
    fields_set = set(fields)
    for field_name in input_fields_list:
        field_name = field_name.strip()[1:] if field_name.startswith("-") else field_name.strip()
        if field_name not in fields_set:
            yield tool.create_text_message(f"Your {validate_type} has invalid field: {field_name}")
            return False
    return True
