import requests
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class AgentapiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        agentapi_url = credentials.get('agentapi_url')
        if not agentapi_url:
            raise ToolProviderCredentialValidationError("AgentAPI Server URL is required.")

        try:
            response = requests.get(f"{agentapi_url}/status")
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ToolProviderCredentialValidationError(f"Failed to connect to AgentAPI server: {e}")