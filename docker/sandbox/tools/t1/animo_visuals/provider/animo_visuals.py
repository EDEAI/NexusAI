from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class AnimoVisualsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            api = credentials.get("animo_api_key")
            x = list(api)
            if x != []:
                print("Animo API Key is valid.") 
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
