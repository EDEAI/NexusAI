from collections.abc import Generator
from typing import Any
import requests
import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamPlayerAchievementsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves the list of achievements for a specific Steam user in a particular game.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamid (str): The 64-bit Steam ID of the player to query achievements for.
                - appid (str): The AppID of the game to query achievements for.
                - language (str, optional): The language for achievement names and descriptions.

        Yields:
            ToolInvokeMessage: A JSON message containing the user's game achievements.

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
            url = f"http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key={api_key}&steamid={steamid}"
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
            
            # Check for API errors
            if 'playerstats' not in data:
                raise Exception("Invalid API response format")
                
            playerstats = data['playerstats']
            
            # Check if there's an error message
            if 'error' in playerstats:
                error_msg = playerstats.get('error', 'Unknown error')
                raise Exception(f"Steam API returned an error: {error_msg}")
                
            # Check if achievement data exists
            if 'achievements' not in playerstats:
                raise Exception("No achievement data found. The user might not own the game or the game might not support achievements")
            
            # Get basic information
            game_name = playerstats.get('gameName', f"AppID: {appid}")
            steam_id = playerstats.get('steamID', steamid)
            achievements = playerstats.get('achievements', [])
            
            if not achievements:
                yield self.create_text_message(f"Steam user {steam_id} has no achievement data for game '{game_name}'")
                return
            
            # Format result
            result = {
                "success": True,
                "steamid": steam_id,
                "game": {
                    "appid": appid,
                    "name": game_name
                },
                "achievement_count": len(achievements),
                "completed_count": sum(1 for a in achievements if a.get('achieved', 0) == 1),
                "achievements": []
            }
            
            # Calculate completion percentage
            if len(achievements) > 0:
                result["completion_percentage"] = round((result["completed_count"] / result["achievement_count"]) * 100, 2)
            
            # Process each achievement
            for achievement in achievements:
                # Convert Unix timestamp to readable format
                unlock_timestamp = achievement.get('unlocktime', 0)
                unlock_date = datetime.datetime.fromtimestamp(unlock_timestamp).strftime('%Y-%m-%d %H:%M:%S') if unlock_timestamp and achievement.get('achieved', 0) == 1 else None
                
                achievement_info = {
                    "apiname": achievement.get('apiname'),
                    "achieved": achievement.get('achieved') == 1,
                    "unlocktime_timestamp": unlock_timestamp if achievement.get('achieved', 0) == 1 else None,
                    "unlocktime_date": unlock_date
                }
                
                # Add optional localized name and description
                if 'name' in achievement:
                    achievement_info["name"] = achievement.get('name')
                    
                if 'description' in achievement:
                    achievement_info["description"] = achievement.get('description')
                
                result["achievements"].append(achievement_info)
            
            # Sort by unlock time (unlocked achievements first, sorted by unlock time in descending order)
            result["achievements"] = sorted(
                result["achievements"],
                key=lambda x: (not x.get('achieved'), -(x.get('unlocktime_timestamp') or 0))
            )
            
        except Exception as e:
            raise Exception(f"Failed to get player achievements: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)