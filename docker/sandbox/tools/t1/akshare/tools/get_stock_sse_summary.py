from collections.abc import Generator
from typing import Any

import akshare as ak
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetStockSseSummaryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """Get summary info of Shanghai Stock Exchange (SSE)"""

        try:
            res = ak.stock_sse_summary()
        except Exception as e:
            yield self.create_text_message(f"Error: {str(e)}")
            yield self.create_json_message({"error": str(e)})
            return

        yield self.create_text_message(str(res))
        yield self.create_json_message({"data": res.to_dict(orient="records")})
