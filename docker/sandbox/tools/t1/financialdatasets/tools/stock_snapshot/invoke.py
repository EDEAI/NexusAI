from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class CryptoSnapshotTool(Tool):
    """
    A tool for querying cryptocurrency snapshot data based on the provided parameters.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the tool to query cryptocurrency snapshot data based on the provided parameters.

        Args:
            tool_parameters (dict[str, Any]): A dictionary containing the following required parameters:
                - "ticker" (str): The cryptocurrency ticker symbol (e.g., "BTC-USD").

        Yields:
            ToolInvokeMessage: A message containing the response from the query, typically in text format.

        Raises:
            KeyError: If any required parameter is missing from the `tool_parameters` dictionary.
        """

        ticker = get_required_parameter(tool_parameters, "ticker")

        resp = http_get(
            credentials=self.runtime.credentials,
            endpoint=Endpoint.STOCK_SNAPSHOT,
            params={"ticker": ticker},
        )

        yield self.create_text_message(resp)
