from typing import Any

from tools.search_web import LinkupSearchTool

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class LinkupProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in LinkupSearchTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "test", "depth": "standard"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
