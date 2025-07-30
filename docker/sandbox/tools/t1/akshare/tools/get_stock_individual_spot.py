from collections.abc import Generator
from typing import Any

import akshare as ak
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetStockIndividualSpotTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        xq_a_token = self.runtime.credentials.get("xq_a_token", "")
        if not xq_a_token:
            raise ValueError("xq_a_token is required but not provided.")

        try:
            res = ak.stock_individual_spot_xq(
                symbol=tool_parameters.get("symbol", "SH600519"),
                token=xq_a_token,
                timeout=30.0,  # Currently set to 30 seconds
            )

        except Exception as e:
            raise e
            yield self.create_text_message(f"Error: {str(e)}")
            yield self.create_json_message({"error": str(e)})
            return

        yield self.create_text_message(str(res))
        yield self.create_json_message(dict(zip(res["item"], res["value"])))
