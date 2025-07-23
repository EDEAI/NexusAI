from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamRecentlyPlayedTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves a list of games a Steam user has played in the last two weeks.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamid (str): The 64-bit Steam ID of the user.
                - count (str, optional): Limit the number of games returned.

        Yields:
            ToolInvokeMessage: A JSON message containing the user's recently played games.

        Raises:
            Exception: If the request fails or the profile is not public.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid.")

        # 2. Get tool input parameters
        steamid = tool_parameters.get("steamid")
        if not steamid:
            raise Exception("Steam ID cannot be empty.")
        
        # Get optional count parameter
        count = tool_parameters.get("count", "")  # Default is empty, which means no limit

        # 3. Call API to perform operation
        try:
            # Build API URL with parameters
            url = f"http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={api_key}&steamid={steamid}&format=json"
            
            # Add count parameter if provided
            if count:
                try:
                    count_value = int(count)
                    if count_value <= 0:
                        raise ValueError("Count must be a positive number")
                    url += f"&count={count_value}"
                except ValueError:
                    raise Exception("Invalid count value. It must be a positive integer.")
            
            response = requests.get(url)
            
            # Check response status code
            if response.status_code == 401:
                raise Exception("API key is invalid or unauthorized.")
            elif response.status_code == 403:
                raise Exception("Access denied. The API key may not have sufficient permissions.")
            elif response.status_code == 404:
                raise Exception("No data found. The user might not exist or the profile is not public.")
            elif response.status_code != 200:
                raise Exception(f"Steam API request failed with status code: {response.status_code}")
            
            # Parse response data
            data = response.json()
            
            # Check if the response format is valid
            if 'response' not in data:
                raise Exception("Invalid API response format.")
            
            # Check if there are any recently played games
            if 'games' not in data['response'] or not data['response']['games']:
                yield self.create_text_message("This Steam user hasn't played any games in the last two weeks or the profile is private.")
                return
            
            games = data['response']['games']
            total_count = data['response'].get('total_count', len(games))
            
            # Format result
            result = {
                "success": True,
                "steamid": steamid,
                "total_count": total_count,
                "games": []
            }
            
            # Process each game
            for game in games:
                game_info = {
                    "appid": game.get('appid'),
                    "name": game.get('name'),
                    "playtime_2weeks": game.get('playtime_2weeks', 0),  # Playtime in last 2 weeks in minutes
                    "playtime_forever": game.get('playtime_forever', 0)  # Total playtime in minutes
                }
                
                # Add image URLs if available
                if 'img_icon_url' in game:
                    icon_hash = game.get('img_icon_url')
                    if icon_hash:
                        game_info["img_icon_url"] = icon_hash
                        game_info["icon_url"] = f"http://media.steampowered.com/steamcommunity/public/images/apps/{game.get('appid')}/{icon_hash}.jpg"
                
                if 'img_logo_url' in game:
                    logo_hash = game.get('img_logo_url')
                    if logo_hash:
                        game_info["img_logo_url"] = logo_hash
                        game_info["logo_url"] = f"http://media.steampowered.com/steamcommunity/public/images/apps/{game.get('appid')}/{logo_hash}.jpg"
                
                # Add human-readable playtime for better readability
                minutes_2weeks = game.get('playtime_2weeks', 0)
                hours_2weeks = minutes_2weeks / 60
                
                if hours_2weeks < 1:
                    game_info["playtime_2weeks_readable"] = f"{minutes_2weeks} minutes"
                else:
                    game_info["playtime_2weeks_readable"] = f"{hours_2weeks:.1f} hours"
                
                minutes_forever = game.get('playtime_forever', 0)
                hours_forever = minutes_forever / 60
                
                if hours_forever < 1:
                    game_info["playtime_forever_readable"] = f"{minutes_forever} minutes"
                else:
                    game_info["playtime_forever_readable"] = f"{hours_forever:.1f} hours"
                
                # Add to games list
                result["games"].append(game_info)
            
            # Sort games by recent playtime (most played first)
            result["games"] = sorted(result["games"], 
                                    key=lambda x: x.get('playtime_2weeks', 0),
                                    reverse=True)
            
        except Exception as e:
            raise Exception(f"Failed to get recently played games: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)