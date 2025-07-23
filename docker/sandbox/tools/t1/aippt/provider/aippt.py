from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from services.aippt_api import grant_token


class AipptProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            print(credentials)
            grant_token(credentials['api_key'], credentials['secret_key'])

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))