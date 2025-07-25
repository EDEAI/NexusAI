from collections.abc import Generator
from typing import Any
from scrapegraph_py import Client

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ScrapeGraphAITool(Tool):
    """
    A tool for web scraping and content extraction using ScrapeGraphAI.
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Execute ScrapeGraphAI operations based on the specified method.

        Args:
            tool_parameters: A dictionary containing the tool input parameters:
                - method (str): The method to use ('smartscraper', 'searchscraper', or 'markdownify')
                - api_key (str): The ScrapeGraphAI API key
                - website_url (str, optional): The URL to scrape (required for smartscraper and markdownify)
                - user_prompt (str): The prompt for extraction or search

        Yields:
            ToolInvokeMessage: A message containing the results of the operation.

        Raises:
            Exception: If the operation fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["scrapegraphai_api_key"]
        except KeyError:
            raise Exception("ScrapeGraphAI API Key is not configured or invalid. Please provide it in the plugin settings.")

        # 2. Get tool input parameters
        method = tool_parameters.get("method")
        website_url = tool_parameters.get("website_url")
        user_prompt = tool_parameters.get("user_prompt")

        if not method:
            raise Exception("Method parameter is required.")
        if not user_prompt:
            raise Exception("User prompt is required.")
        if method in ["smartscraper", "markdownify"] and not website_url:
            raise Exception("Website URL is required for smartscraper and markdownify methods.")

        # 3. Initialize ScrapeGraphAI client
        try:
            client = Client(api_key=api_key)
        except Exception as e:
            raise Exception(f"Failed to initialize ScrapeGraphAI client: {e}")

        # 4. Execute the requested method
        try:
            if method == "smartscraper":
                response = client.smartscraper(
                    website_url=website_url,
                    user_prompt=user_prompt
                )
            elif method == "searchscraper":
                response = client.searchscraper(
                    user_prompt=user_prompt
                )
            elif method == "markdownify":
                response = client.markdownify(
                    website_url=website_url
                )
            else:
                raise Exception(f"Unknown method: {method}")
        except Exception as e:
            raise Exception(f"ScrapeGraphAI operation failed: {e}")

        # 5. Return results
        yield self.create_text_message(str(response))