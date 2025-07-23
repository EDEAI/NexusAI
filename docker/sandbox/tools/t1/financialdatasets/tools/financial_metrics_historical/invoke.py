from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class FinancialMetricsHistoricalTool(Tool):
    """
    A tool for retrieving historical financial metrics based on a given ticker symbol.
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
        period = get_required_parameter(tool_parameters, "period")
        limit = tool_parameters.get("limit", None)

        resp = http_get(
            credentials=self.runtime.credentials,
            endpoint=Endpoint.FINANCIAL_METRICS_HISTORICAL,
            params={"ticker": ticker, "period": period, "limit": limit},
        )
        yield self.create_text_message(resp)
