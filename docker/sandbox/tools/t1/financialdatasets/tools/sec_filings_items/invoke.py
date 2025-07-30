from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import Endpoint, get_required_parameter, http_get


class SECFilingsItemsTool(Tool):
    """
    A tool for retrieving SEC filings items based on a given ticker symbol and filing date.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the tool with the provided parameters and yields a response message.

        Args:
            tool_parameters (dict[str, Any]): A dictionary containing the parameters
                required for the tool. Must include the "ticker" and "filing_date" keys.

        Yields:
            ToolInvokeMessage: A message containing the response from the query.

        Raises:
            ValueError: If the "ticker" or "filing_date" parameters are missing from tool_parameters.
        """

        ticker = get_required_parameter(tool_parameters, "ticker")
        filing_type = get_required_parameter(tool_parameters, "filing_type")
        year = get_required_parameter(tool_parameters, "year")
        qaurter = tool_parameters.get("qaurter", None)
        item = tool_parameters.get("item", None)

        resp = http_get(
            credentials=self.runtime.credentials,
            endpoint=Endpoint.SEC_FILINGS_ITEMS,
            params={
                "ticker": ticker,
                "filing_type": filing_type,
                "year": year,
                "qaurter": qaurter,
                "item": item,
            },
        )
        yield self.create_text_message(resp)
