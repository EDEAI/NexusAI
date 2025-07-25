from typing import Any

from dify_plugin import ToolProvider

class JustWaitProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        # 这个provider不需要验证凭据，因为我们不需要任何外部API
        pass 