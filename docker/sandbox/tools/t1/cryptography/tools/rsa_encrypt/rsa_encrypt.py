import base64
from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RsaEncryptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        plaintext: str = tool_parameters.get("plaintext")
        if not plaintext or not isinstance(plaintext, str):
            raise ValueError("Not a valid file for input input_file")

        public_key_text: str = tool_parameters.get("public_key_text")
        if not public_key_text and not "BEGIN PUBLIC KEY" in public_key_text:
            raise ValueError("Invalid RSA public key string, which should be starts with '-----BEGIN PUBLIC KEY-----'")

        try:
            public_key = serialization.load_pem_public_key(public_key_text.encode("utf-8"))
        except ValueError as e:
            raise ValueError("Failed to load public key from PEM format") from e

        try:
            encrypted_bytes = self.encrypt_data(public_key=public_key, plaintext=plaintext.encode())
            result_base64_str = base64.b64encode(encrypted_bytes).decode("utf-8")
            yield self.create_text_message(result_base64_str)
        except ValueError as e:
            raise ValueError(
                "Failed to encrypt data, as its length is too large for the provided RSA public key") from e

    @staticmethod
    def encrypt_data(public_key, plaintext: bytes) -> bytes:
        ciphertext = public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
