from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.nominatim_search import NominatimSearchTool
from dify_plugin import ToolProvider


class NominatimProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in NominatimSearchTool.from_credentials(credentials).invoke(
                tool_parameters={"query": "London", "limit": 1}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
