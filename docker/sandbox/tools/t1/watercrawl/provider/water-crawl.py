import re
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from requests import HTTPError

from tools.api import WaterCrawlAPIClient


class WaterCrawlProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        base_url = credentials["base_url"] or "https://app.watercrawl.dev/"

        if not self.validate_url(base_url):
            raise ToolProviderCredentialValidationError("Invalid base URL")

        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            response = WaterCrawlAPIClient(credentials["api_key"], base_url).get_crawl_requests_list(page_size=1)
            if 'results' not in response:
                raise ToolProviderCredentialValidationError("Invalid URL or API key")
        except HTTPError as e:
            if e.response.status_code == 401:
                raise ToolProviderCredentialValidationError("Invalid API key")
            if e.response.status_code == 404:
                raise ToolProviderCredentialValidationError("Invalid base URL")
            raise e
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

    def validate_url(self, url):
        try:
            regex = re.compile(
                    r'^(https?:\/\/)+' # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
                    r'localhost|' #localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
                    r'(?::\d+)?' # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            return url if bool(re.match(regex, url)) else None
        except Exception:
            return False
