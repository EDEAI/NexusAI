import json
from typing import Any


def parse_json(input_string: str) -> dict[str, Any]:
    try:
        return json.loads(input_string)
    except Exception as e:
        raise ValueError(f"Failed to parse JSON: {str(e)}")
