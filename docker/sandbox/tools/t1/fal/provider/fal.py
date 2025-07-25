import requests
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class FalProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        url = "https://fal.run/fal-ai/flux/dev"
        headers = {"Authorization": f"Key {credentials.get('fal_api_key')}", "Content-Type": "application/json"}
        data = {"prompt": "Cat"}
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 401:
            raise ToolProviderCredentialValidationError("FAL API key is invalid")
        elif response.status_code != 200:
            raise ToolProviderCredentialValidationError(f"FAL API key validation failed: {response.text}")