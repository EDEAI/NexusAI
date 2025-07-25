from collections.abc import Generator
from typing import Any

# Remove the import for encrypt_message as EncryptTool is removed
# from utils.the_gpg import encrypt_message

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Keep the import for sign_message
from utils.the_gpg import sign_message

# Keep only the SignTool class
class SignTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invokes the GPG signing tool.
        """
        message_to_sign = tool_parameters.get("message_to_sign")
        private_key_str = tool_parameters.get("signer_private_key_str")
        passphrase = tool_parameters.get("passphrase") # Optional

        if not message_to_sign or not private_key_str:
            yield self.create_text_message("Error: Message to sign and private key are required.")
            return

        try:
            # Call the utility function
            signature_blob = sign_message(
                plaintext=message_to_sign,
                private_key_str=private_key_str,
                passphrase=passphrase # Pass passphrase if provided
            )

            # Return the signature as text and potentially JSON/variable
            yield self.create_text_message(f"Detached Signature:\n```\n{signature_blob}\n```")
            yield self.create_json_message({"signature": signature_blob})
            # yield self.create_variable_message("gpg_signature", signature_blob) # Optional: if needed for workflows

        except ValueError as ve:
            # Handle specific errors from the utility function (e.g., bad key, wrong passphrase)
            yield self.create_text_message(f"Signing Error: {str(ve)}")
        except Exception as e:
            # Handle unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during signing: {str(e)}")
