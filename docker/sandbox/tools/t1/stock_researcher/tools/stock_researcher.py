# File: dify-stock-plugin/tools/stock_researcher.py
# This file contains the core Python logic for the "Stock Researcher" tool.
# It simulates fetching real-time stock prices for a given symbol.

from collections.abc import Generator
from typing import Any, Mapping
import requests 

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class StockResearcherTool(Tool):
    """
    A Dify Tool Plugin to fetch (simulated) real-time stock prices.
    In a real-world scenario, this would integrate with a financial API.
    """

    def _invoke(self, tool_parameters: Mapping[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        Invokes the stock price retrieval.

        Args:
            tool_parameters (Mapping[str, Any]): A dictionary containing the tool's input parameters.
                Expected keys:
                - "symbol" (str): The stock symbol (e.g., "AAPL", "MSFT"). (required)

        Yields:
            ToolInvokeMessage: A JSON message containing the stock price information.
            ToolInvokeMessage: Text messages for progress or errors.
        """
        symbol = tool_parameters.get("query")

        if not symbol:
            yield self.create_text_message("Error: Missing required parameter 'symbol'.")
            return

        yield self.create_text_message(f"Fetching real-time price for {symbol.upper()}...")

        

        api_key = self.runtime.credentials.get("financial_api_key")
        if not api_key:
            yield self.create_text_message("Error: Financial API key is not configured.")
            return
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"Error fetching stock data: {e}")
            return


        # Prepare the structured output
        result = data

        # Yield the results as a JSON message
        yield self.create_json_message({"stock_info": result})
        yield self.create_text_message(f"Successfully retrieved price for {symbol.upper()}.")

