from collections.abc import Generator
from typing import Any
import requests
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamOwnedGamesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves a list of games owned by a Steam user.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamid (str): The 64-bit Steam ID of the user.
                - include_appinfo (str, optional): Include game name and logo information.
                - include_played_free_games (str, optional): Include free games that have been played.
                - appids_filter (str, optional): JSON array of appids to filter the results.

        Yields:
            ToolInvokeMessage: A JSON message containing the user's owned games.

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
        
        # Get optional parameters with default values
        include_appinfo = tool_parameters.get("include_appinfo", "true").lower() == "true"
        include_played_free_games = tool_parameters.get("include_played_free_games", "true").lower() == "true"
        
        # Parse appids_filter if provided
        appids_filter = []
        appids_filter_param = tool_parameters.get("appids_filter", "")
        if appids_filter_param:
            try:
                # Try to parse as JSON array
                appids_filter = json.loads(appids_filter_param)
                if not isinstance(appids_filter, list):
                    raise Exception("appids_filter must be a JSON array of app IDs.")
            except json.JSONDecodeError:
                raise Exception("Invalid JSON format for appids_filter. Example: [440, 570, 730]")

        # 3. Call API to perform operation
        try:
            # Build base URL with required parameters
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steamid}&format=json"
            
            # Add optional parameters
            if include_appinfo:
                url += "&include_appinfo=1"
            if include_played_free_games:
                url += "&include_played_free_games=1"
            
            # If appids_filter is provided, it needs to be sent as POST data
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = None
            
            if appids_filter:
                data = {"appids_filter": appids_filter}
                response = requests.post(url, data=json.dumps(data), headers=headers)
            else:
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
            
            # Check if games data is available
            if 'games' not in data['response']:
                # This could mean the profile is private or the user has no games
                if 'game_count' in data['response'] and data['response']['game_count'] == 0:
                    yield self.create_text_message("This Steam user doesn't own any games or all games are filtered out.")
                else:
                    yield self.create_text_message("Unable to retrieve game list. The user's profile might be private.")
                return
            
            games = data['response']['games']
            game_count = data['response'].get('game_count', len(games))
            
            # Format result
            result = {
                "success": True,
                "steamid": steamid,
                "game_count": game_count,
                "games": []
            }
            
            # Process each game
            for game in games:
                game_info = {
                    "appid": game.get('appid'),
                    "playtime_forever": game.get('playtime_forever', 0),  # Total playtime in minutes
                }
                
                # Include playtime in last 2 weeks if available
                if 'playtime_2weeks' in game:
                    game_info["playtime_2weeks"] = game.get('playtime_2weeks', 0)  # Playtime in last 2 weeks in minutes
                
                # Add optional info if available and if include_appinfo was true
                if include_appinfo:
                    if 'name' in game:
                        game_info["name"] = game.get('name')
                    
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
                
                # Add has_community_visible_stats if available
                if 'has_community_visible_stats' in game:
                    game_info["has_community_visible_stats"] = game.get('has_community_visible_stats')
                    # Add stats page URL if stats are available
                    if game.get('has_community_visible_stats'):
                        game_info["stats_url"] = f"http://steamcommunity.com/profiles/{steamid}/stats/{game.get('appid')}"
                
                # Add to games list
                result["games"].append(game_info)
            
            # Sort games by playtime (most played first)
            result["games"] = sorted(result["games"], 
                                   key=lambda x: x.get('playtime_forever', 0),
                                   reverse=True)
            
            # Add human-readable playtime for better readability
            for game in result["games"]:
                minutes_forever = game.get('playtime_forever', 0)
                hours_forever = minutes_forever / 60
                
                if hours_forever < 1:
                    game["playtime_readable"] = f"{minutes_forever} minutes"
                else:
                    game["playtime_readable"] = f"{hours_forever:.1f} hours"
                
                if "playtime_2weeks" in game:
                    minutes_2weeks = game.get('playtime_2weeks', 0)
                    hours_2weeks = minutes_2weeks / 60
                    
                    if hours_2weeks < 1:
                        game["playtime_2weeks_readable"] = f"{minutes_2weeks} minutes"
                    else:
                        game["playtime_2weeks_readable"] = f"{hours_2weeks:.1f} hours"
            
        except Exception as e:
            raise Exception(f"Failed to get owned games: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)