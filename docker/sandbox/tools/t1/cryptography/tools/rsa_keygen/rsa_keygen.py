from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class RsaKeygenTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        key_size: int = int(tool_parameters.get("key_size", 2048))
        if not key_size in [2048, 3072, 4096]:
            raise ValueError("key_size must be one of [2048, 3072, 4096]")

        private_key_pem, public_key_pem = self.generate_rsa_key_pair(key_size)

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
    def generate_rsa_key_pair(key_size=2048) -> (bytes, bytes):
        """
        生成 RSA 密钥对并返回 PEM 格式的私钥和公钥
        :param key_size: 密钥长度（推荐 2048 位或更高）
        :return: (private_key_pem, public_key_pem)
        """
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
        )
        public_key = private_key.public_key()

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
            # TODO: password protection（eg. serialization.BestAvailableEncryption(b'password')）
        )
        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        return private_key_pem, public_key_pem
