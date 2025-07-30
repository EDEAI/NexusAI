import base64
from collections.abc import Generator
from typing import Any

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class AesDecryptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        ciphertext: str = tool_parameters.get("ciphertext")
        if not ciphertext or not isinstance(ciphertext, str):
            raise ValueError("Not a valid file for input input_file")

        key_text: str = tool_parameters.get("key_text")
        if not key_text or not isinstance(key_text, str):
            raise ValueError("Encryption key is required")
        key_bytes: bytes = base64.b64decode(key_text.encode())
        if len(key_bytes) not in [16, 24, 32]:
            raise ValueError(f"Invalid decoded AES key length {len(key_bytes)}, which must be either 16, 24, or 32")

        try:
            base64_decoded_ciphertext = base64.urlsafe_b64decode(ciphertext.encode("utf-8"))
        except Exception as e:
            raise ValueError("Ciphertext is not valid base64 encoding") from e

        if len(base64_decoded_ciphertext) < 16:
            raise ValueError("Ciphertext too short, missing IV or data.")
        if (len(base64_decoded_ciphertext) - 16) % 16 != 0:
            raise ValueError(
                "Ciphertext length (excluding IV) is not a multiple of block size (16 bytes). Possible data corruption or wrong input.")

        try:
            decrypted_bytes = self.decrypt_data(key=key_bytes,
                                                encrypted_data=base64_decoded_ciphertext)
            result_str = decrypted_bytes.decode("utf-8")
            yield self.create_text_message(result_str)
        except ValueError as e:
            raise ValueError("Failed to decrypt data") from e

    @staticmethod
    def decrypt_data(key: bytes, encrypted_data: bytes) -> bytes:
        iv = encrypted_data[:16]
        ciphertext = encrypted_data[16:]

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()

        padded_data = decryptor.update(ciphertext) + decryptor.finalize()

        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted_data = unpadder.update(padded_data) + unpadder.finalize()

        return decrypted_data
