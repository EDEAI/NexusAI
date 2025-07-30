from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class FinancialMetricsSnapshotTool(Tool):
    """
    A tool for retrieving financial metrics snapshot based on a given ticker symbol.
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

        resp = http_get(
            credentials=self.runtime.credentials,
            endpoint=Endpoint.FINANCIAL_METRICS_SNAPSHOT,
            params={"ticker": ticker},
        )
        yield self.create_text_message(resp)
