from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from ragflow_api import auth

class RagflowApiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            auth(credentials)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
