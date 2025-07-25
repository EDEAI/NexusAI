from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.rabbit_utils import get_rabbit_client

class RabbitSendPluginProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            get_rabbit_client(credentials)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
