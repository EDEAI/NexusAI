from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class StockPricesTool(Tool):
    """
    A tool for retrieving stock prices based on a given ticker symbol.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the tool with the provided parameters and yields a response message.

        Args:
            tool_parameters (dict[str, Any]): A dictionary containing the parameters
                required for the tool. Must include the "ticker" key.

        Yields:
            ToolInvokeMessage: A message containing the response from the query.

        Raises:
            ValueError: If the "ticker" parameter is missing from tool_parameters.
        """

        ticker = get_required_parameter(tool_parameters, "ticker")
        interval = get_required_parameter(tool_parameters, "interval")
        interval_multiplier = get_required_parameter(
            tool_parameters, "interval_multiplier"
        )
        start_date = get_required_parameter(tool_parameters, "start_date")
        end_date = get_required_parameter(tool_parameters, "end_date")
        limit = tool_parameters.get("limit", None)

        resp = http_get(
            credentials=self.runtime.credentials,
            endpoint=Endpoint.STOCK_PRICES,
            params={
                "ticker": ticker,
                "interval": interval,
                "interval_multiplier": interval_multiplier,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
        )
        yield self.create_text_message(resp)
