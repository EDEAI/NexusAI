from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.parse import EasyDocTool

class EasydocProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            instance = EasyDocTool.from_credentials(credentials)
            assert isinstance(instance, EasyDocTool)
            instance.validate_token()
            pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))