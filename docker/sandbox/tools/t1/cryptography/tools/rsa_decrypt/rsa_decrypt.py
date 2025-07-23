import base64
from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RsaDecryptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        ciphertext: str = tool_parameters.get("ciphertext")
        if not ciphertext or not isinstance(ciphertext, str):
            raise ValueError("Not a valid file for input input_file")

        private_key_text: str = tool_parameters.get("private_key_text")
        if not private_key_text and not "BEGIN PRIVATE KEY" in private_key_text:
            raise ValueError(
                "Invalid RSA private key string, which should be starts with '-----BEGIN PRIVATE KEY-----'")

        try:
            private_key = serialization.load_pem_private_key(data=private_key_text.encode("utf-8"), password=None)
        except ValueError as e:
            raise ValueError("Failed to load private key from PEM format") from e

        try:
            decrypted_bytes = self.decrypt_data(private_key=private_key,
                                                ciphertext=base64.b64decode(ciphertext.encode("utf-8")))
            result_base64_str = decrypted_bytes.decode("utf-8")
            yield self.create_text_message(result_base64_str)
        except ValueError as e:
            raise ValueError("Failed to decrypt data") from e

    @staticmethod
    def decrypt_data(private_key, ciphertext: bytes) -> bytes:
        ciphertext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return ciphertext
