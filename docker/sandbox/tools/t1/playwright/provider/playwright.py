from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.playwright import run_playwright


class PlaywrightProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            run_playwright(credentials.get("playwright_uri"), "")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
