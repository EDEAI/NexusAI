from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from utils import create_opensearch_client


class OpensearchProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            client = create_opensearch_client(credentials)
            client.info()
        except Exception as e:
            raise ToolProviderCredentialValidationError(repr(e))
