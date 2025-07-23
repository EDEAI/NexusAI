from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.util import parse_cookies, search_bilibili


class BilibiliProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            cookies: str = credentials.get("cookies")
            if not cookies:
                raise ToolProviderCredentialValidationError(
                    "Missing cookies in credentials"
                )

            _ = search_bilibili(
                keyword="Dify",
                page=1,
                cookies=parse_cookies(cookies),
            )

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
