from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.the_gpg import verify_message

class VerifyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Invokes the GPG verification tool."""
        original_message = tool_parameters.get('original_message')
        signature_blob = tool_parameters.get('signature_blob')
        signer_pubkey_str = tool_parameters.get('signer_pubkey_str')

        # Basic validation
        if not original_message:
            yield self.create_text_message("Error: Original message is required.")
            return
        if not signature_blob:
            yield self.create_text_message("Error: Signature blob is required.")
            return
        if not signer_pubkey_str:
            yield self.create_text_message("Error: Signer public key is required.")
            return
        if '-----BEGIN PGP SIGNATURE-----' not in signature_blob:
             yield self.create_text_message("Error: Signature blob appears invalid (missing header).")
             return
        if '-----BEGIN PGP PUBLIC KEY BLOCK-----' not in signer_pubkey_str:
             yield self.create_text_message("Error: Signer public key appears invalid (missing header).")
             return

        try:
            # Call the verification function from the_gpg.py
            is_valid = verify_message(
                original_message=original_message,
                signature_blob=signature_blob,
                signer_pubkey_str=signer_pubkey_str
            )

            # Return the result as text and potentially JSON/variable
            result_text = "Signature is VALID." if is_valid else "Signature is INVALID."
            yield self.create_text_message(result_text)
            yield self.create_json_message({"is_valid": is_valid})
            # yield self.create_variable_message("gpg_verification_result", is_valid) # Optional

        except ValueError as ve:
            # Handle specific errors from the utility function (e.g., bad key/signature format)
            yield self.create_text_message(f"Verification Error: {str(ve)}")
        except Exception as e:
            # Handle unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during verification: {str(e)}")
