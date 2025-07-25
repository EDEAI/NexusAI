from typing import Any, Tuple

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


def get_config(credentials: dict[str, Any]) -> Tuple[dict[str, Any], dict[str, Any]]:
    db_config = {
        "database": credentials.get("db_name"),
        "user": credentials.get("db_user"),
        "password": credentials.get("db_password"),
        "host": credentials.get("db_host"),
        "port": credentials.get("db_port"),
    }
    # 检查配置完整性
    required_fields = ["database", "user", "password", "host", "port"]
    missing_fields = [field for field in required_fields if not db_config[field]]
    if missing_fields:
        raise ValueError(
            f"Missing required configuration fields: {', '.join(missing_fields)}"
        )

    config = {
        "max_fetched_rows": credentials.get("max_fetched_rows"),
    }
    max_fetched_rows: str = config["max_fetched_rows"]
    if max_fetched_rows:
        if isinstance(max_fetched_rows, int) or max_fetched_rows.isnumeric():
            config["max_fetched_rows"] = int(max_fetched_rows)
        else:
            raise ValueError(f"Bad max_fetched_rows={max_fetched_rows}")
    return db_config, config


class DifyDbToolProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            get_config(credentials)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
