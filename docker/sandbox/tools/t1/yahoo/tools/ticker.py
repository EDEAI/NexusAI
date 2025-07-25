from collections.abc import Generator
from typing import Any
from requests.exceptions import HTTPError, ReadTimeout
from yfinance import Ticker
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class YahooFinanceSearchTickerTool(Tool):
    def _invoke(
        self,tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        invoke tools
        """
        query = tool_parameters.get("symbol", "")
        if not query:
            yield self.create_text_message("Please input symbol")
            return
        try:
            yield self.create_json_message(self.run(ticker=query))
        except (HTTPError, ReadTimeout):
            yield self.create_text_message("There is a internet connection problem. Please try again later.")

    def run(self, ticker: str) -> dict[str, Any]:
        return Ticker(ticker).info
