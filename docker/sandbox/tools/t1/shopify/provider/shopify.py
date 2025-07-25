from typing import Any

from requests import post

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class ShopifyProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            store_id = credentials.get("shopify_store_id")
            password = credentials.get("shopify_app_password")
            res = post(
                f"https://{store_id}.myshopify.com/admin/api/unstable/graphql.json",
                json={"query": "{ __type(name: \"App\") { name } }"},
                headers={
                    "X-Shopify-Access-Token": password,
                    "Content-Type": "application/json",
                },
            )
            r = res.json()
            if "errors" in r:
                raise Exception(f"Error: {r['errors']}")
            pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
