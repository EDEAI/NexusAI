from typing import Any

import httpx
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SmallPayProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        url = "https://pay.freecicoda.com/smallPayment/api/v1/order/createOrder"

        payload = {
            "apiKey": credentials.get("api_key"),
            "title": "测试订单",
            "desc": "测试描述",
            "money": 100
            }

        try:
            res = httpx.post(url, json=payload).json()
            if res.get("code") != 200:
                raise ToolProviderCredentialValidationError(res.get("message"))
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
