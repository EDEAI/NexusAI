from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamNewsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves the latest news for a specified game.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - appid (str): The AppID of the game.
                - count (str, optional): Number of news entries to return. Default is 3.
                - maxlength (str, optional): Maximum length of each news entry. Default is 300.

        Yields:
            ToolInvokeMessage: A JSON message containing the game news.

        Raises:
            Exception: If the request fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid. Please provide it in the plugin settings.")

        # 2. Get tool input parameters
        appid = tool_parameters.get("appid")
        if not appid:
            raise Exception("Game AppID cannot be empty.")
        
        # Get optional parameters with default values
        count = tool_parameters.get("count", "3")
        maxlength = tool_parameters.get("maxlength", "300")

        # 3. Call API to perform operation
        try:
            url = f"http://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/?appid={appid}&count={count}&maxlength={maxlength}&format=json"
            response = requests.get(url)
            
            # Check response status code
            if response.status_code != 200:
                raise Exception(f"Steam API request failed with status code: {response.status_code}")
            
            # Parse response data
            data = response.json()
            
            # Check if news data exists
            if 'appnews' not in data or 'newsitems' not in data['appnews']:
                raise Exception("Invalid API response format")
            
            # Get news data
            appnews = data['appnews']
            newsitems = appnews['newsitems']
            
            if not newsitems:
                yield self.create_text_message(f"No news found for game ID {appid}")
                return
            
            # Format result
            result = {
                "success": True,
                "appid": appnews.get('appid'),
                "news_count": len(newsitems),
                "newsitems": []
            }
            
            # Process each news item
            for item in newsitems:
                news_item = {
                    "gid": item.get('gid'),
                    "title": item.get('title'),
                    "url": item.get('url'),
                    "author": item.get('author'),
                    "contents": item.get('contents'),
                    "date": item.get('date'),
                    "feedlabel": item.get('feedlabel'),
                    "feed_name": item.get('feed_name')
                }
                result["newsitems"].append(news_item)
            
        except Exception as e:
            raise Exception(f"Failed to get game news: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)