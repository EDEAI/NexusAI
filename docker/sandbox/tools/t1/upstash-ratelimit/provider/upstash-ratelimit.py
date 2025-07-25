from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import requests

class UpstashRatelimitProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            upstash_url = credentials.get("UPSTASH_REDIS_REST_URL")
            upstash_token = credentials.get("UPSTASH_REDIS_REST_TOKEN")

            if not upstash_url or not upstash_token:
                raise ToolProviderCredentialValidationError("Missing Upstash credentials: UPSTASH_REDIS_REST_URL or UPSTASH_REDIS_REST_TOKEN.")

            test_key = "dify_plugin_test"
            test_value = "validate"
            response = requests.get(
                f"{upstash_url}/set/{test_key}/{test_value}",
                headers={"Authorization": f"Bearer {upstash_token}"},
            )

            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"Failed to authenticate with Upstash: {response.text}")

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
