from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.brave_search import BraveSearchTool
from dify_plugin import ToolProvider


class BraveProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in BraveSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "Sachin Tendulkar"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
