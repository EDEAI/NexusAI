from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.query_stock import QueryStockTool
from dify_plugin import ToolProvider


class AlphaVantageProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            QueryStockTool.from_credentials(credentials, user_id="").invoke(tool_parameters={"code": "AAPL"})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
