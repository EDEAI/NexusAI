from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider

from spiderApp import Spider


class SpiderProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            app = Spider(api_key=credentials["spider_api_key"])
            app.scrape_url(url="https://spider.cloud")
        except AttributeError as e:
            if "NoneType" in str(e) and "not iterable" in str(e):
                raise ToolProviderCredentialValidationError("API is currently down, try again in 15 minutes", str(e))
            else:
                raise ToolProviderCredentialValidationError("An unexpected error occurred.", str(e))
        except Exception as e:
            raise ToolProviderCredentialValidationError("An unexpected error occurred.", str(e))
