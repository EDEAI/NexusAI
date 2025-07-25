from typing import Any

import akshare as ak
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class XueqiuProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            """
            IMPLEMENT YOUR VALIDATION HERE
            """
            xq_a_token: str = credentials.get("xq_a_token", "")
            if not xq_a_token:
                raise ToolProviderCredentialValidationError("xq_a_token is required")

            res = ak.stock_individual_basic_info_xq(
                symbol="SH600519",
                token=xq_a_token,
                timeout=30.0,  # Currently set to 30 seconds
            )

            assert dict(zip(res["item"], res["value"])).get("org_id") == "03130028"

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
