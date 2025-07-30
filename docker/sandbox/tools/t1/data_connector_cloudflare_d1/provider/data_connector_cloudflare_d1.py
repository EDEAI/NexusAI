from typing import Any

from tools.cloudflare_verify import CloudflareVerify

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class DataConnectorCloudflareD1Provider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in CloudflareVerify.from_credentials(credentials).invoke(
                tool_parameters={
                    "a_cloudflare_api_token": ""
                }
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
