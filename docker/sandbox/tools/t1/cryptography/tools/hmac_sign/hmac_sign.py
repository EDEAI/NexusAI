import base64
import logging
from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.hashes import HashAlgorithm
from cryptography.hazmat.primitives.hmac import HMAC
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.hmac_sign.hmac_algorithm import HmacAlgorithm


class HmacSignTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        algorithm: str = tool_parameters.get("algorithm")
        plaintext: str = tool_parameters.get("plaintext")
        key: str = tool_parameters.get("key")
        output_encoding: str = tool_parameters.get("output_encoding", "hex")
        if not plaintext:
            raise ValueError("No invalid input for parameter plaintext")
        if not key:
            raise ValueError("No invalid input for parameter key")
        if not algorithm:
            raise ValueError("No invalid input for parameter algorithm")
        hash_algorithm_instance: HashAlgorithm
        match algorithm.upper():
            case HmacAlgorithm.HMAC_SHA1:
                hash_algorithm_instance = hashes.SHA1()
            case HmacAlgorithm.HMAC_SHA256:
                hash_algorithm_instance = hashes.SHA256()
            case _:
                raise ValueError(f"Unsupported algorithm: {algorithm}, only"
                                 f" {HmacAlgorithm.HMAC_SHA1}, {HmacAlgorithm.HMAC_SHA256} are supported")

        try:
            hmac_result_bytes = self.generate_hmac(
                key=key.encode("utf-8"),
                message=plaintext.encode("utf-8"),
                hash_algorithm=hash_algorithm_instance,
            )

            result_str: str
            match output_encoding.lower():
                case "base64":
                    result_str = base64.b64encode(hmac_result_bytes).decode("utf-8")
                case "hex":
                    result_str = hmac_result_bytes.hex()
                case _:
                    result_str = ""

            yield self.create_text_message(result_str)
        except:
            logging.exception("Failed to generate HMAC signature")

    def generate_hmac(self, key: bytes, message: bytes, hash_algorithm: HashAlgorithm) -> bytes:
        h = HMAC(key, hash_algorithm)
        h.update(message)
        return h.finalize()
