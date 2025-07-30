from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from utils.common_utils import get_redis_connection


class RedisToolProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            conn = get_redis_connection(credentials)
            res = conn.ping()
            if not res:
                raise ToolProviderCredentialValidationError(str(res))
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
