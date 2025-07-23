from collections.abc import Generator
from typing import Any

# Import the specific function from your utils file
# Only import decrypt_message here
from utils.the_gpg import decrypt_message

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Keep only the DecryptTool class
class DecryptTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Invokes the GPG decryption tool."""
        encrypted_message_str = tool_parameters.get('encrypted_message_str')
        private_key_str = tool_parameters.get('private_key_str')
        passphrase = tool_parameters.get('passphrase') # Optional

        # Basic validation
        if not encrypted_message_str:
            yield self.create_text_message("Error: Encrypted message is required.")
            return
        if not private_key_str:
            yield self.create_text_message("Error: Private key is required.")
            return
        if '-----BEGIN PGP MESSAGE-----' not in encrypted_message_str:
            yield self.create_text_message("Error: Encrypted message appears invalid (missing header).")
            return
        if '-----BEGIN PGP PRIVATE KEY BLOCK-----' not in private_key_str:
            yield self.create_text_message("Error: Private key appears invalid (missing header).")
            return

        try:
            # Call the decryption function from the_gpg.py
            decrypted_message = decrypt_message(
                ciphertext=encrypted_message_str,
                private_key_str=private_key_str,
                passphrase=passphrase
            )

            # Return the decrypted message as text output
            yield self.create_text_message(decrypted_message)
            # Optionally, return as JSON if you defined an output schema
            # yield self.create_json_message({'decrypted_message': decrypted_message})

        except ValueError as ve:
            # Catch specific ValueErrors raised by decrypt_message (e.g., bad key, wrong passphrase)
            yield self.create_text_message(f"Decryption Error: {ve}")
        except Exception as e:
            # Catch any other unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during decryption: {e}")
