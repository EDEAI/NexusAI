import requests
from yarl import URL
from core.tool.errors import ToolCertificateVerification

class BaseAuthorization:
    def sd_validate_credentials(self, credentials: dict):
        """
        Validates the provided credentials by checking the presence of an API key
        and verifying it against the Stability API.

        :param credentials: A dictionary containing the API key.
        :raises ToolCertificateVerification: If the API key is missing or invalid.
        :return: True if the credentials are valid.
        """
        api_key = credentials.get('api_key', '')
        if not api_key:
            raise ToolCertificateVerification('API key is required.')

        response = requests.get(
            URL('https://api.stability.ai') / 'v1' / 'user' / 'account',
            headers=self.generate_authorization_headers(credentials),
            timeout=(5, 30)
        )

        if not response.ok:
            raise ToolCertificateVerification('Invalid API key.')

        return True

    def generate_authorization_headers(self, credentials: dict) -> dict[str, str]:
        """
        Generates the authorization headers required for API requests.

        :param credentials: A dictionary containing the API key.
        :return: A dictionary with the authorization header.
        """
        return {
            'Authorization': f'Bearer {credentials.get("api_key", "")}'
        }