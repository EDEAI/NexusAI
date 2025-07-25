from collections.abc import Generator
from typing import Any

# Correct import
from utils.the_gpg import generate_key_pair
# Import PubKeyAlgorithm and EllipticCurveOID if needed for type conversion/validation
from pgpy.constants import PubKeyAlgorithm, EllipticCurveOID

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

# Class name is already correct: GenerateKeyTool
class GenerateKeyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Invokes the GPG key generation tool."""
        # Get parameters using correct names from YAML
        real_name = tool_parameters.get('real_name')
        email = tool_parameters.get('email')
        passphrase = tool_parameters.get('passphrase') # Optional, defaults to None if not present
        key_type_str = tool_parameters.get('key_type') # Optional, e.g., "EdDSA"
        key_param_str = tool_parameters.get('key_param') # Optional, e.g., "Ed25519" or "3072"

        # Basic validation
        if not real_name or not email:
            yield self.create_text_message("Error: Real name and email are required for key generation.")
            return

        # --- Parameter Conversion/Validation (Optional but Recommended) ---
        key_type_enum = PubKeyAlgorithm.EdDSA # Default
        if key_type_str:
            try:
                # Use dictionary-style access instead of .get()
                key_type_enum = PubKeyAlgorithm[key_type_str]
            except KeyError: # Catch KeyError for invalid names
                yield self.create_text_message(f"Error: Invalid key_type '{key_type_str}'.")
                return

        key_param_parsed = None
        if key_param_str:
            # Try parsing as integer first (for RSA/DSA lengths)
            try:
                key_param_parsed = int(key_param_str)
            except ValueError:
                # If not integer, try parsing as EllipticCurveOID (for EdDSA/ECDSA curves)
                try:
                    # Use dictionary-style access instead of .get()
                    key_param_parsed = EllipticCurveOID[key_param_str]
                except KeyError: # Catch KeyError for invalid names
                    yield self.create_text_message(f"Error: Invalid key_param '{key_param_str}'. Could not parse as integer or curve name.")
                    return
        # --- End Parameter Conversion ---

        try:
            # Call the utility function with all parameters
            # Pass the parsed enum/value or None if not provided
            private_key, public_key = generate_key_pair(
                real_name=real_name,
                email=email,
                passphrase=passphrase,
                key_type=key_type_enum,
                key_param=key_param_parsed
            )

            # Output using JSON message matching the output_schema
            output_data = {
                "public_key": public_key,
                "private_key": private_key # Handle with care - consider security implications
            }
            yield self.create_json_message(output_data)
            # Optionally, add a simple text confirmation
            yield self.create_text_message("GPG key pair generated successfully.")
            # Optionally, yield variables if needed for workflows
            # yield self.create_variable_message("public_key", public_key)
            # yield self.create_variable_message("private_key", private_key)


        except ValueError as ve:
             # Catch specific validation errors from the_gpg.py or parameter parsing
             yield self.create_text_message(f"Key generation error: {ve}")
        except RuntimeError as rte:
             # Catch runtime errors from the_gpg.py
             yield self.create_text_message(f"Key generation failed: {rte}")
        except Exception as e:
            # Catch any other unexpected errors
            yield self.create_text_message(f"An unexpected error occurred during key generation: {e}")
