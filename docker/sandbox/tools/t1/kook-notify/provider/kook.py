from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.client import get_me


class DifyPluginPdmTemplateProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Test using /api/v3/user/me
            get_me(credentials)

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
