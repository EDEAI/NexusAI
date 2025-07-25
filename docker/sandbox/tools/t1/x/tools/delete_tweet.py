from collections.abc import Generator
from typing import Any

import requests
from requests_oauthlib import OAuth1Session
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DeleteTweetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Delete a tweet using the X API
        """
        # Extract tweet_id from parameters
        tweet_id = tool_parameters.get("tweet_id")
        
        if not tweet_id:
            yield self.create_text_message("Error: Tweet ID is required")
            return
        
        try:
            # Get credentials from runtime
            credentials = self.runtime.credentials
            
            # Create OAuth1 session
            oauth = OAuth1Session(
                credentials["api_key"],
                client_secret=credentials["api_secret"],
                resource_owner_key=credentials["access_token"],
                resource_owner_secret=credentials["access_token_secret"]
            )
            
            # Endpoint URL for deleting tweets
            url = f"https://api.twitter.com/2/tweets/{tweet_id}"
            
            # Delete the tweet
            response = oauth.delete(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                response_data = response.json()
                deleted = response_data.get("data", {}).get("deleted", False)
                
                if deleted:
                    # Return success message
                    yield self.create_json_message({
                        "status": "success",
                        "message": f"Tweet with ID {tweet_id} deleted successfully"
                    })
                else:
                    yield self.create_text_message(f"Failed to delete tweet with ID {tweet_id}. Response: {response_data}")
            else:
                error_message = f"Failed to delete tweet. Status code: {response.status_code}, Response: {response.text}"
                yield self.create_text_message(error_message)
                
        except Exception as e:
            error_message = f"Error deleting tweet: {str(e)}"
            yield self.create_text_message(error_message)