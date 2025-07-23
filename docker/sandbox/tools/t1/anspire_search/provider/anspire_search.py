from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.anspire_search import AnspireSearchTool


class AnspireSearchProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
             for _ in AnspireSearchTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "test"},
            ):
                 pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
