from collections.abc import Generator
from typing import Any, Optional, Mapping

import jwt
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import jwt_utils


class JwtEncoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        param_payload: str = tool_parameters.get("payload", "{}") or "{}"
        param_headers: str = tool_parameters.get("headers")
        key: str = tool_parameters.get("key")
        algorithm: str = tool_parameters.get("algorithm")

        # validation
        jwt_utils.check_valid_algorithm(algorithm)
        if not key:
            raise ValueError("Invalid input for decryption key")

        payload: Mapping[str, Any] = jwt_utils.parse_valid_json(param_payload, "payload")
        headers: Optional[Mapping[str, Any]] = jwt_utils.parse_valid_json(param_headers, "headers") \
            if param_headers else None
        result: str = jwt.encode(payload=payload, key=key, algorithm=algorithm, headers=headers)

        yield self.create_text_message(result)
