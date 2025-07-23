from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import snowflake.connector

class SnowflakeProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            conn = snowflake.connector.connect(
                account=credentials.get("account"),
                user=credentials.get("user"),
                password=credentials.get("password"),
                warehouse=credentials.get("warehouse", None),
                role=credentials.get("role", None),
            )

            conn.cursor().execute("SELECT CURRENT_VERSION()")

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
        
        finally:
            conn.close()
