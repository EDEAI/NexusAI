from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.openapi.client import OpenAPIClient
from tools.openapi.urls import FOTOR_OPENAPI_VALIDATE_API_KEY


class DifyPluginBrokerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate the credentials for the Dify Plugin Broker provider.
        :param credentials: Credentials dictionary containing the API key.
        :return: None
        """

        try:
            client = OpenAPIClient(
                api_key=credentials['fotor_openapi_key'],
                validate_api_key_url=credentials['fotor_openapi_endpoint'] + FOTOR_OPENAPI_VALIDATE_API_KEY,
            )

            if not client.validate_api_key():
                raise ToolProviderCredentialValidationError("Fotor API key is invalid")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
