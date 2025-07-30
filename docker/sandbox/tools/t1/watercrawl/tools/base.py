from tools.api import WaterCrawlAPIClient


class WaterCrawlBaseMixin:
    """Base tool for WaterCrawl"""

    @property
    def client(self) -> WaterCrawlAPIClient:
        return WaterCrawlAPIClient(
            self.runtime.credentials["api_key"],
            self.runtime.credentials["base_url"] or "https://app.watercrawl.dev/",
        )

    def get_safe_array(self, params, key):
        value = params.get(key, '').strip()
        if not value:
            return []

        if isinstance(value, list):
            return value

        if ',' in value:
            return value.split(',')

        return [value]
