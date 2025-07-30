from collections.abc import Generator
from typing import Any
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamPlayerDetailsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves detailed profile information for multiple Steam users.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamids (str): Comma-separated list of Steam IDs, up to 100.

        Yields:
            ToolInvokeMessage: A JSON message containing detailed Steam user profiles.

        Raises:
            Exception: If the request fails, an exception with error information is thrown.
        """
        # 1. Get credentials from runtime
        try:
            api_key = self.runtime.credentials["api_key"]
        except KeyError:
            raise Exception("Steam API Key is not configured or invalid. Please provide it in the plugin settings.")

        # 2. Get tool input parameters
        steamids = tool_parameters.get("steamids")
        if not steamids:
            raise Exception("Steam ID cannot be empty.")
        
        # Check if the number of IDs exceeds the limit
        id_list = steamids.split(',')
        if len(id_list) > 100:
            raise Exception("You can query a maximum of 100 Steam IDs at once.")

        # 3. Call API to perform operation
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steamids}"
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
                yield self.create_text_message(f"No Steam users found with the specified IDs: {steamids}")
                return
            
            # Format result
            result = {
                "success": True,
                "player_count": len(players),
                "players": []
            }
            
            # Handle player status mapping
            persona_states = {
                0: "Offline",
                1: "Online",
                2: "Busy",
                3: "Away",
                4: "Snooze",
                5: "Looking to Trade",
                6: "Looking to Play"
            }
            
            # Process detailed information for each player
            for player in players:
                # Get status description
                state_num = player.get('personastate', 0)
                state_desc = persona_states.get(state_num, "Unknown")
                
                # Build detailed player profile
                player_info = {
                    # Public data
                    "steamid": player.get('steamid'),
                    "personaname": player.get('personaname'),
                    "profileurl": player.get('profileurl'),
                    "avatar": player.get('avatar'),
                    "avatarmedium": player.get('avatarmedium'),
                    "avatarfull": player.get('avatarfull'),
                    "personastate": state_num,
                    "personastate_desc": state_desc,
                    "communityvisibilitystate": player.get('communityvisibilitystate'),
                    "profilestate": player.get('profilestate'),
                    "lastlogoff": player.get('lastlogoff'),
                    "commentpermission": player.get('commentpermission'),
                    
                    # Private data (if available)
                    "realname": player.get('realname'),
                    "primaryclanid": player.get('primaryclanid'),
                    "timecreated": player.get('timecreated'),
                    "gameid": player.get('gameid'),
                    "gameserverip": player.get('gameserverip'),
                    "gameextrainfo": player.get('gameextrainfo'),
                    "loccountrycode": player.get('loccountrycode'),
                    "locstatecode": player.get('locstatecode'),
                    "loccityid": player.get('loccityid')
                }
                
                # Filter out None values
                player_info = {k: v for k, v in player_info.items() if v is not None}
                
                result["players"].append(player_info)
            
        except Exception as e:
            raise Exception(f"Failed to get player profiles: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)