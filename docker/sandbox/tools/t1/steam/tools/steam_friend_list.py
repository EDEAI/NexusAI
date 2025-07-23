from collections.abc import Generator
from typing import Any
import requests
import datetime

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SteamFriendListTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Retrieves the friend list of a specified Steam user. Note: The user's Steam profile must be set to "Public" to access the friend list.

        Args:
            tool_parameters: A dictionary containing tool input parameters:
                - steamid (str): The 64-bit Steam ID of the user whose friend list to retrieve.
                - relationship (str, optional): Relationship filter. Possible values: all, friend. Default is friend.

        Yields:
            ToolInvokeMessage: A JSON message containing the user's friend list.

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
        
        # Get optional parameters with default values
        relationship = tool_parameters.get("relationship", "friend")
        if relationship not in ["all", "friend"]:
            raise Exception("The relationship parameter must be 'all' or 'friend'.")

        # 3. Call API to perform operation
        try:
            url = f"http://api.steampowered.com/ISteamUser/GetFriendList/v0001/?key={api_key}&steamid={steamid}&relationship={relationship}"
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
            
            # Check if friend data exists
            if 'friendslist' not in data or 'friends' not in data['friendslist']:
                raise Exception("Invalid API response format or the user has no friends")
            
            friends = data['friendslist']['friends']
            
            if not friends:
                yield self.create_text_message(f"Steam ID {steamid} has no friends or the profile is not public")
                return
            
            # Format result
            result = {
                "success": True,
                "steamid": steamid,
                "relationship_filter": relationship,
                "friend_count": len(friends),
                "friends": []
            }
            
            # Process each friend's information
            for friend in friends:
                # Convert Unix timestamp to readable format
                friend_since_timestamp = friend.get('friend_since', 0)
                friend_since_date = datetime.datetime.fromtimestamp(friend_since_timestamp).strftime('%Y-%m-%d %H:%M:%S') if friend_since_timestamp else None
                
                friend_info = {
                    "steamid": friend.get('steamid'),
                    "relationship": friend.get('relationship'),
                    "friend_since_timestamp": friend_since_timestamp,
                    "friend_since_date": friend_since_date
                }
                result["friends"].append(friend_info)
            
            # Sort by friendship establishment time (newest to oldest)
            result["friends"] = sorted(result["friends"], 
                                     key=lambda x: x.get('friend_since_timestamp', 0),
                                     reverse=True)
            
        except Exception as e:
            raise Exception(f"Failed to get friend list: {str(e)}")

        # 4. Return result
        yield self.create_json_message(result)