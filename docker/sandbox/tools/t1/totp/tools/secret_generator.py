from collections.abc import Generator
from typing import Any

import pyotp

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SecretGenerator(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        secret_key = pyotp.random_base32()
        yield self.create_text_message(secret_key)
        try:
            name = tool_parameters["name"]
            issuer_name = tool_parameters["issuer_name"]
        except KeyError:
            name = None
            issuer_name = None
        if name or issuer_name:
            provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(name=name, issuer_name=issuer_name)
            yield self.create_variable_message("provisioning_uri", provisioning_uri)
        else:
            pass