from typing import Any
import requests
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class AirtableProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if "airtable_token" not in credentials or not credentials.get("airtable_token"):
                raise ToolProviderCredentialValidationError("airtable_token is required")
            try:
                headers = {
                    "Authorization": f"Bearer {credentials['airtable_token']}",
                }
                response = requests.get(url="https://api.airtable.com/v0/meta/whoami", headers=headers)
                if response.status_code != 200:
                    raise ToolProviderCredentialValidationError("airtable_token is invalid")
            except Exception as e:
                raise ToolProviderCredentialValidationError("Air table token is invalid. {}".format(e))
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
