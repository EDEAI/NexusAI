from typing import Any

import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from sandbox_fusion.common import trim_slash


class SandboxfusionProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            SANDBOX_FUSION_ENDPOINT = credentials.get(
                "SANDBOX_FUSION_ENDPOINT", "http://localhost:8080"
            )
            if not SANDBOX_FUSION_ENDPOINT:
                raise ToolProviderCredentialValidationError(
                    "SANDBOX_FUSION_ENDPOINT is required"
                )

            result = requests.get(f"{trim_slash(SANDBOX_FUSION_ENDPOINT)}/v1/ping")

            assert result.text == '"pong"'

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
