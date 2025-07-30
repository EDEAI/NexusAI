from collections.abc import Generator
from typing import Any

import akshare as ak
import regex as re
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetStockHistoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # symbol: str = "SH600519",
        # period: str = "daily",
        # start_date: str = "19700101",
        # end_date: str = "20500101",
        # adjust: str = "",
        # timeout: float = None,

        symbol = tool_parameters.get(
            "symbol", "600519"
        )  # No need to add "SH" or "SZ" prefix here
        # save numbers only
        symbol = re.sub(r"[^0-9]", "", symbol)

        period = tool_parameters.get(
            "period", "daily"
        )  # choice of {'daily', 'weekly', 'monthly'}
        start_date = tool_parameters.get("start_date", "20240101")
        end_date = tool_parameters.get("end_date", "20500101")

        # The default return is unadjusted data;
        # qfq: returns data adjusted for forward stock splits (forward-adjusted data);
        # hfq: returns data adjusted for backward stock splits (backward-adjusted data).
        adjust = tool_parameters.get("adjust", "")

        try:
            res = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust,
                timeout=30.0,  # Currently set to 30 seconds
            )
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
            yield self.create_json_message({"error": str(e)})
            return

        yield self.create_text_message(str(res))
        yield self.create_json_message(
            {
                "data": res.to_dict(orient="records"),
            }
        )
