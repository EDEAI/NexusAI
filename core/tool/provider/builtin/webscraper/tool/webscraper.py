import json
import traceback
from core.tool.provider.builtin_tool_provider import BuiltinTool
from core.workflow.variables import ObjectVariable, Variable
import re
import httpx

class WebscraperTool(BuiltinTool):
    """
    A tool for scraping web content using specified URL and regular expressions.
    """

    def get_url(self, url: str, user_agent: str, method: str, regular: dict):
        """
        Fetches the content of a URL and extracts data using regular expressions.

        :param url: The URL to fetch.
        :param user_agent: The User-Agent string to use for the request.
        :param method: The HTTP method to use (GET, POST, etc.).
        :param regular: A dictionary of regular expressions to apply to the web content.
        :return: A dictionary of matched results.
        :raises Exception: If the URL cannot be fetched or if the status code is not 200.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.1000.0 Safari/537.36"
        }
        if user_agent:
            headers["User-Agent"] = user_agent

        # Use GET by default unless specified otherwise
        method = method.upper() if method else "GET"

        try:
            response = httpx.request(url=url, method=method, headers=headers)
            print(response)

            if response.status_code != 200:
                raise Exception(f"Failed to fetch the URL: {url}, status code: {response.status_code}")

            web_content = response.text
            print(web_content)
            # Match results stored in a dictionary
            matched_results = {}
            for key, pattern in regular.items():
                matches = re.finditer(pattern, web_content)
                matched_results[key] = tuple(match.group() for match in matches)

            return matched_results
        except Exception as e:
            print(f"Error fetching URL: {str(e)}")
            raise

    def _invoke(self, tool_parameters: ObjectVariable) -> Variable:
        """
        Invokes the web scraping tool with the given parameters.

        :param tool_parameters: An ObjectVariable containing the parameters for the tool.
        :return: A Variable containing the JSON result of the web scraping.
        :raises ValueError: If required parameters are missing.
        :raises Exception: If an error occurs during the invocation.
        """
        try:
            tool_parameters_dict = {
                key: value.value
                for key, value in tool_parameters.properties.items()
                if value.value is not None
            }
            url = tool_parameters_dict.get('url', '')
            user_agent = tool_parameters_dict.get('user_agent', '')
            regular = tool_parameters_dict.get('regular')

            if not url:
                raise ValueError('Please input url')
            if not regular:
                raise ValueError('Please input regular')

            # Get webpage
            result = self.get_url(url=url, user_agent=user_agent, method='POST', regular=json.loads(regular))
            return Variable(name='text', type="json", value=json.dumps(result), display_name='Output text')
        except Exception as e:
            print(traceback.format_exc())
            raise e