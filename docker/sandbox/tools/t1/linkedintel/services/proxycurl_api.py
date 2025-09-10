import requests


class ProxycurlApiException(Exception):
    def __init__(self, message: str, code: int | None = None):
        self.message = message
        self.code = code
        super().__init__(message)

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


class ProxycurlAPI:
    def __init__(self, api_key: str):
        if not api_key or not isinstance(api_key, str):
            raise ProxycurlApiException("Missing or invalid Proxycurl API key.")
        self.api_key = api_key
        self.base_url = "https://nubela.co/proxycurl/api/v2/linkedin"

    def enrich_profile(self, linkedin_url: str) -> dict:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            params = {
                "url": linkedin_url,
                "use_cache": "if-present"
            }

            response = requests.get(self.base_url, headers=headers, params=params)

            if not response.ok:
                raise ProxycurlApiException(response.text, response.status_code)

            return response.json()

        except requests.RequestException as e:
            raise ProxycurlApiException(f"Request error: {str(e)}")
        except Exception as e:
            raise ProxycurlApiException(f"[Unexpected Error] {str(e)}")
