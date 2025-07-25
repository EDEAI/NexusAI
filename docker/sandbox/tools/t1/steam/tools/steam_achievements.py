from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamAchievementsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves global achievement completion percentage data for a specific game.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - gameid (str): The AppID of the game.

        Yields:
            ToolInvokeMessage: A JSON message containing the game achievement percentage data.

        Raises:
            Exception: If the request fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid.")

        # 2. Get tool input parameters
        gameid = tool_parameters.get("gameid")
        if not gameid:
            raise Exception("Game AppID cannot be empty.")

        # 3. Call API to perform operation
        try:
            url = f"http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid={gameid}&format=json"
            response = requests.get(url)
            
            # Check response status code
            if response.status_code != 200:
                raise Exception(f"Steam API request failed with status code: {response.status_code}")
            
            # Parse response data
            data = response.json()
            
            # Check if achievement data exists
            if 'achievementpercentages' not in data or 'achievements' not in data['achievementpercentages']:
                raise Exception("Invalid API response format")
            
            # Get achievement data
            achievements = data['achievementpercentages']['achievements']
            
            if not achievements:
                yield self.create_text_message(f"No achievement data found for game ID {gameid}")
                return
            
            # Format result
            result = {
                "success": True,
                "gameid": gameid,
                "achievement_count": len(achievements),
                "achievements": []
            }
            
            # Process each achievement
            for achievement in achievements:
                achievement_data = {
                    "name": achievement.get('name'),
                    "percent": achievement.get('percent')
                }
                result["achievements"].append(achievement_data)
            
            # Sort by completion rate (high to low)
            result["achievements"] = sorted(result["achievements"], 
                                          key=lambda x: x.get('percent', 0),
                                          reverse=True)
            
        except Exception as e:
            raise Exception(f"Failed to get game achievement data: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)