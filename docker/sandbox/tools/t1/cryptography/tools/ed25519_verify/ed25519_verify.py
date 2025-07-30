import base64
import logging
from collections.abc import Generator
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class Ed25519VerificationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        plaintext: str = tool_parameters.get("plaintext")
        if not plaintext or not isinstance(plaintext, str):
            raise ValueError("Not an valid input for plaintext")

        signature: str = tool_parameters.get("signature")
        if not signature or not isinstance(signature, str):
            raise ValueError("Not an valid input for input signature")

        public_key_text: str = tool_parameters.get("public_key_text")
        if not public_key_text and not "PUBLIC KEY" in public_key_text:
            raise ValueError(
                "Invalid Ed25519 public key string, which should be starts with '-----BEGIN PUBLIC KEY-----'")

        try:
            public_key: Ed25519PublicKey = serialization.load_pem_public_key(public_key_text.encode("utf-8"))
        except ValueError as e:
            raise ValueError("Failed to load Ed25519 public key from PEM format") from e

        try:
            self.verify_signature(
                public_key=public_key,
                data=plaintext.encode(),
                signature=base64.b64decode(signature.encode("utf-8")),
            )
            yield self.create_text_message(str(True))
        except InvalidSignature:
            yield self.create_text_message(str(False))
            logging.exception("Invalid signature")
        except ValueError:
            yield self.create_text_message(str(False))
            logging.exception("Invalid signature")

    @staticmethod
    def verify_signature(public_key: Ed25519PublicKey, data: bytes, signature: bytes):
        """
        Sign the data and return a 64 byte signature
        """
        try:
            public_key.verify(signature=signature, data=data)
        except InvalidSignature as e:
            raise ValueError("Invalid signature") from e
