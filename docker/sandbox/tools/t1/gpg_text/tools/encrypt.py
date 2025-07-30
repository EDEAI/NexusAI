from collections.abc import Generator
from typing import Any

# Import the specific function from your utils file
from utils.the_gpg import encrypt_message

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Rename the class to reflect the tool's purpose
class EncryptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Invokes the GPG encryption tool."""
        plaintext = tool_parameters.get('plaintext')
        recipient_pubkey_str = tool_parameters.get('recipient_pubkey_str')

        # Basic validation
        if not plaintext:
            yield self.create_text_message("Error: Plaintext message is required.")
            return
        if not recipient_pubkey_str:
            yield self.create_text_message("Error: Recipient public key is required.")
            return
        if '-----BEGIN PGP PUBLIC KEY BLOCK-----' not in recipient_pubkey_str:
             yield self.create_text_message("Error: Recipient public key appears invalid (missing header).")
             return

        try:
            # Call the encryption function from the_gpg.py
            encrypted_message_str = encrypt_message(plaintext, recipient_pubkey_str)

            # Return the encrypted message as text output
            yield self.create_text_message(encrypted_message_str)
            # Optionally, return as JSON if you defined an output schema
            # yield self.create_json_message({'encrypted_message': encrypted_message_str})

        except ValueError as ve:
            # Catch specific ValueErrors raised by encrypt_message for better feedback
            yield self.create_text_message(f"Encryption Error: {ve}")
        except Exception as e:
            # Catch any other unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during encryption: {e}")
