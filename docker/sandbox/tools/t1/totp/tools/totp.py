from collections.abc import Generator
from typing import Any

from utils.totp_verify import verify_totp

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TotpTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Accepts either a secret key or a provisioning URI (otpauth://)
        secret_key = tool_parameters["secret_key"]
        totp_code = tool_parameters["user_code"]
        
        result = verify_totp(secret_key, totp_code)
        
        yield self.create_json_message(result)
        
        if result["status"] == "success":
            yield self.create_text_message("Valid")
            yield self.create_variable_message("True_or_False", "True")
        else:
            yield self.create_text_message("Invalid")
            yield self.create_variable_message("True_or_False", "False")