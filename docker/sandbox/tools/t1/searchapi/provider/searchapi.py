from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.google import GoogleTool
from dify_plugin import ToolProvider


class SearchAPIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            GoogleTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "SearchApi dify", "result_type": "link"}
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
