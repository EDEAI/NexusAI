from typing import Any
import requests

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class SteamProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # Get API Key
            api_key = credentials.get("api_key")
            if not api_key:
                raise ToolProviderCredentialValidationError("Steam API Key cannot be empty")
            
            # Get Steam ID
            steam_id = credentials.get("steam_id")
            if not steam_id:
                raise ToolProviderCredentialValidationError("Steam ID cannot be empty")
            
            # Make API call to validate credentials
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
            response = requests.get(url)
            
            # Validate response status code
            if response.status_code != 200:
                raise ToolProviderCredentialValidationError(f"API validation failed with status code: {response.status_code}")
            
            # Check API response format
            response_data = response.json()
            if 'response' not in response_data or 'players' not in response_data['response']:
                raise ToolProviderCredentialValidationError("Invalid API response format")
            
            # Verify if the specified user was found
            players = response_data['response']['players']
            if not players:
                raise ToolProviderCredentialValidationError(f"No Steam user found with ID: {steam_id}")
                
        except ToolProviderCredentialValidationError:
            # Directly re-raise custom validation errors
            raise
        except Exception as e:
            # Handle other possible errors
            raise ToolProviderCredentialValidationError(f"Credential validation failed: {str(e)}")
    
    def get_player_summary(self, steam_id: str) -> dict:
        """Get Steam user profile information"""
        api_key = self.credentials.get('api_key')
        if not api_key:
            return {"success": False, "message": "API Key does not exist"}
        
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
            response = requests.get(url)
            
            if response.status_code != 200:
                return {"success": False, "message": f"Steam API request failed: HTTP status code {response.status_code}"}
            
            data = response.json()
            
            if 'response' not in data or 'players' not in data['response']:
                return {"success": False, "message": "Invalid API response format"}
            
            players = data['response']['players']
            if not players:
                return {"success": False, "message": f"No Steam user found with ID: {steam_id}"}
            
            player = players[0]
            return {
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
            return {"success": False, "message": f"Failed to get player profile: {str(e)}"}
