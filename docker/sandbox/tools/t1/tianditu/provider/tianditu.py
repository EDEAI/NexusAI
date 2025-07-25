from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.poisearch import PoiSearchTool
from dify_plugin import ToolProvider


class TiandituProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            PoiSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"content": "北京", "specify": "156110000"}
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
