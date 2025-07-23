from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.send_to_bark import SendNotify2Bark


class BarkNotifyProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for resp in SendNotify2Bark.from_credentials(credentials).invoke(
                    {"content": "test push from Dify bark-notify tool plugin"}):
                if resp.message.json_object.get("code", -1) != 200:
                    raise ToolProviderCredentialValidationError(resp.message.json_object.get("message"))
        except ToolProviderCredentialValidationError as e:
            raise e
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
