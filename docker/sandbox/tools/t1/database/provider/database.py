from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.sql_execute import SQLExecuteTool


class DatabaseProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        if not credentials.get("db_uri"):
            return
        query = "SELECT 1 FROM DUAL" if "oracle" in credentials.get("db_uri") else "SELECT 1"
        try:
            for _ in SQLExecuteTool.from_credentials(credentials).invoke(
                tool_parameters={"query": query}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
