from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamUserStatsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves detailed game statistics for a Steam user in a specific game.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamid (str): The 64-bit Steam ID of the player to query statistics for.
                - appid (str): The AppID of the game to query statistics for.
                - language (str, optional): The language for returned data.

        Yields:
            ToolInvokeMessage: A JSON message containing the user's game statistics.

        Raises:
            Exception: If the request fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid. Please provide it in the plugin settings.")

        # 2. Get tool input parameters
        steamid = tool_parameters.get("steamid")
        if not steamid:
            raise Exception("Steam ID cannot be empty.")
        
        appid = tool_parameters.get("appid")
        if not appid:
            raise Exception("Game AppID cannot be empty.")
        
        # Get optional parameters
        language = tool_parameters.get("language", "")  # Default is empty, using Steam's default language

        # 3. Call API to perform operation
        try:
            # Build API URL, including optional language parameter
            url = f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid={appid}&key={api_key}&steamid={steamid}"
            if language:
                url += f"&l={language}"
                
            response = requests.get(url)
            
            # Check response status code
            if response.status_code == 401:
                raise Exception("API key is invalid or unauthorized.")
            elif response.status_code == 403:
                raise Exception("Access denied. The API key may not have sufficient permissions.")
            elif response.status_code == 404:
                raise Exception("No data found. The user might not exist, doesn't own the game, or has a private profile.")
            elif response.status_code != 200:
                raise Exception(f"Steam API request failed with status code: {response.status_code}")
            
            # Parse response data
            data = response.json()
            
            # Check API response format
            if 'playerstats' not in data:
                raise Exception("Invalid API response format")
                
            playerstats = data['playerstats']
            
            # Check if there's an error message
            if 'error' in playerstats:
                error_msg = playerstats.get('error', 'Unknown error')
                raise Exception(f"Steam API returned an error: {error_msg}")
            
            # Get game name and player information
            game_name = playerstats.get('gameName', f"AppID: {appid}")
            steam_id = playerstats.get('steamID', steamid)
            
            # Get statistics data
            stats = playerstats.get('stats', [])
            achievements = playerstats.get('achievements', [])
            
            if not stats and not achievements:
                yield self.create_text_message(f"Steam user {steam_id} has no available statistics for game '{game_name}'")
                return
            
            # Format result
            result = {
                "success": True,
                "steamid": steam_id,
                "game": {
                    "appid": appid,
                    "name": game_name
                }
            }
            
            # Add statistics data
            if stats:
                result["stats_count"] = len(stats)
                result["stats"] = []
                
                for stat in stats:
                    stat_info = {
                        "name": stat.get('name'),
                        "value": stat.get('value')
                    }
                    result["stats"].append(stat_info)
            
            # Add achievement data
            if achievements:
                result["achievement_count"] = len(achievements)
                result["completed_count"] = sum(1 for a in achievements if a.get('achieved', 0) == 1)
                
                # Calculate completion percentage
                if len(achievements) > 0:
                    result["completion_percentage"] = round((result["completed_count"] / result["achievement_count"]) * 100, 2)
                
                result["achievements"] = []
                
                for achievement in achievements:
                    achievement_info = {
                        "name": achievement.get('name'),
                        "achieved": achievement.get('achieved') == 1
                    }
                    result["achievements"].append(achievement_info)
            
        except Exception as e:
            raise Exception(f"Failed to get user game statistics: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)