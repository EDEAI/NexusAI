import base64
from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class Ed25519SigningTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        plaintext: str = tool_parameters.get("plaintext")
        if not plaintext or not isinstance(plaintext, str):
            raise ValueError("Not an valid input for plaintext")

        private_key_text: str = tool_parameters.get("private_key_text")
        if not private_key_text and not "PRIVATE KEY" in private_key_text:
            raise ValueError(
                "Invalid Ed25519 private key string, which should be starts with '-----BEGIN PRIVATE KEY-----'")

        try:
            private_key: Ed25519PrivateKey = serialization.load_pem_private_key(
                data=private_key_text.encode("utf-8"),
                password=None)
        except ValueError as e:
            raise ValueError("Failed to load Ed25519 private key from PEM format") from e

        try:
            signature_bytes = self.sign_data(private_key=private_key, data=plaintext.encode())
            result_base64_str = base64.b64encode(signature_bytes).decode("utf-8")
            yield self.create_text_message(result_base64_str)
        except ValueError as e:
            raise e

    @staticmethod
    def sign_data(private_key: Ed25519PrivateKey, data: bytes) -> bytes:
        """
        Sign the data and return a 64 byte signature
        """
        signature = private_key.sign(data=data)
        return signature
