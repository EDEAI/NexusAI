from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.searxng_search import SearXNGSearchTool
from dify_plugin import ToolProvider


class SearXNGProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in SearXNGSearchTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "SearXNG", "limit": 1, "search_type": "general"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
