import json
import logging
from collections.abc import Generator
from typing import Any

import jwt
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.utils import jwt_utils


class JwtDecoderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        param_jwt: str = tool_parameters.get("jwt")
        key: str = tool_parameters.get("key")
        algorithm: str = tool_parameters.get("algorithm")

        # validation
        jwt_utils.check_valid_algorithm(algorithm)
        if not param_jwt:
            raise ValueError("Invalid input JWT token")
        if not key:
            raise ValueError("Invalid input for decryption key")

        try:
            decoded_payload: dict[str, Any] = jwt.decode(jwt=param_jwt, key=key, algorithms=[algorithm])
            extract_headers: bool = ("true" == tool_parameters.get("extract_headers", "false"))
            if extract_headers:
                headers_obj = jwt.get_unverified_header(param_jwt)
                if headers_obj and not decoded_payload.get("_headers"):
                    decoded_payload["_headers"] = headers_obj

            payload_str: str = json.dumps(decoded_payload)

            yield self.create_text_message(payload_str)

        except jwt.ExpiredSignatureError as e:
            logging.exception("Failed to decode JWT token")
            raise RuntimeError(f"Failed to decode JWT token, error: {str(e)}")
