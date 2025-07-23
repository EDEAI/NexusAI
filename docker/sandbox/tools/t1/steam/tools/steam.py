from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves user information based on the provided Steam ID.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steam_id (str): 17-digit Steam ID.

        Yields:
            ToolInvokeMessage: A JSON message containing user information.

        Raises:
            Exception: If the request fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid. Please provide it in the plugin settings.")

        # 2. Get tool input parameters
        steam_id = tool_parameters.get("steam_id")
        if not steam_id:
            raise Exception("Steam ID cannot be empty.")

        # 3. Call API to perform operation
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
            response = requests.get(url)
            
            # Check response status code
            if response.status_code != 200:
                raise Exception(f"Steam API request failed with status code: {response.status_code}")
            
            # Parse response data
            data = response.json()
            
            # Check if player data exists
            if 'response' not in data or 'players' not in data['response']:
                raise Exception("Invalid API response format")
            
            players = data['response']['players']
            if not players:
                raise Exception(f"No Steam user found with ID: {steam_id}")
            
            # Get player data
            player = players[0]
            result = {
                "success": True,
                "player": {
                    "steamid": player.get('steamid'),
                    "personaname": player.get('personaname'),
                    "profileurl": player.get('profileurl'),
                    "avatar": player.get('avatar'),
                    "avatarmedium": player.get('avatarmedium'),
                    "avatarfull": player.get('avatarfull'),
                    "personastate": player.get('personastate'),
                    "lastlogoff": player.get('lastlogoff'),
                    "timecreated": player.get('timecreated'),
                    "communityvisibilitystate": player.get('communityvisibilitystate')
                }
            }
            
        except Exception as e:
            raise Exception(f"Failed to get player profile: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)
