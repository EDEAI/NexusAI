from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class CryptoPricesTool(Tool):
    """
    A tool for querying cryptocurrency price data based on the provided parameters.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the tool to query cryptocurrency price data based on the provided parameters.

        Args:
            tool_parameters (dict[str, Any]): A dictionary containing the following required parameters:
                - "ticker" (str): The cryptocurrency ticker symbol (e.g., "BTC-USD").
                - "interval" (str): The time interval for the price data (e.g., "minute", "day").
                - "interval_multiplier" (int): The multiplier for the interval (e.g., 1, 2).
                - "start_date" (str): The start date for the data query in ISO 8601 format (e.g., "2025-01-01").
                - "end_date" (str): The end date for the data query in ISO 8601 format (e.g., "2025-01-31").
                - "limit" (Optional[int]): The maximum number of data points to retrieve (default is None).

        Yields:
            ToolInvokeMessage: A message containing the response from the query, typically in text format.

        Raises:
            KeyError: If any required parameter is missing from the `tool_parameters` dictionary.
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
            endpoint=Endpoint.CRYPTO_PRICES,
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
