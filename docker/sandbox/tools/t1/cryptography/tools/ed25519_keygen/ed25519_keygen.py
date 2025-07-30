from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class Ed25519KeygenTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        private_key_pem, public_key_pem = self.generate_ed25519_key_pair()

        yield self.create_blob_message(
            blob=private_key_pem,
            meta={
                "mime_type": "application/x-pem-file",
                "filename": "private_key.pem",
            },
        )

        yield self.create_blob_message(
            blob=public_key_pem,
            meta={
                "mime_type": "application/x-pem-file",
                "filename": "public_key.pem",
            },
        )

    @staticmethod
    def generate_ed25519_key_pair() -> (bytes, bytes):
        private_key: Ed25519PrivateKey = Ed25519PrivateKey.generate()
        public_key: Ed25519PublicKey = private_key.public_key()

        private_key_pem: bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        public_key_pem: bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_pem, public_key_pem
