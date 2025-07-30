from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class RsshubProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # RSSHub不需要凭据
        pass
