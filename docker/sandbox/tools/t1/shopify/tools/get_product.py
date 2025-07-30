from collections.abc import Generator
from typing import Any

from requests import post

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

product_query = """
query ($identifier: ProductIdentifierInput!) {
  product: productByIdentifier(identifier: $identifier) {
    handle
    title
    descriptionHtml
    description
    createdAt
    updatedAt
    onlineStoreUrl
    status
    priceRangeV2 {
      maxVariantPrice {
        amount
        currencyCode
      }
      minVariantPrice {
        amount
        currencyCode
      }
    }
    featuredMedia {
      preview {
        image {
          url
        }
      }
    }
    media(first: 30) {
      nodes {
        mediaContentType
        preview {
          image {
            url
          }
        }
      }
    }
    variants(first: 30)  {
      nodes{
        displayName
        price
        image {
          url
        }
      }
    }
  }
}
"""

class ShopifyGetProductTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        store_id = self.runtime.credentials.get("shopify_store_id")
        if not store_id:
            raise Exception("shopify_store_id is required")
        password = self.runtime.credentials.get("shopify_app_password")
        if not password:
            raise Exception("shopify_app_password is required")
        
        indentifier = tool_parameters.get("identifier")
        if not indentifier:
            raise Exception("identifier is required")
        
        is_id_identifier = str(indentifier).isdigit()

        res = post(
            f"https://{store_id}.myshopify.com/admin/api/unstable/graphql.json",
            json={
            "query": product_query,
            "variables": {
                "identifier": {
                    "id" if is_id_identifier else "handle": "gid://shopify/Product/"+indentifier if is_id_identifier else indentifier
                }
            }
            },
            headers={
            "X-Shopify-Access-Token": password,
            "Content-Type": "application/json",
            },
        )
        r = res.json()
        if "errors" in r:
            raise Exception(f"Error: {r['errors']}")
        
        if not r["data"]["product"]:
            raise Exception(f"Product not found, {r}")

        product = r["data"]["product"]
        product["variants"] = product["variants"]["nodes"]
        product["media"] = product["media"]["nodes"]
        yield self.create_json_message(product)
