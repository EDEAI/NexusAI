from collections.abc import Generator
from typing import Any

import requests
from requests_oauthlib import OAuth1Session
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class PostTweetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        Post a tweet using the X API
        """
        # Extract text from parameters
        text = tool_parameters.get("text")
        
        if not text:
            yield self.create_text_message("Error: Tweet text is required")
            return
        
        if len(text) > 280:
            yield self.create_text_message("Error: Tweet text must be 280 characters or less")
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
            
            # Endpoint URL for posting tweets
            url = "https://api.twitter.com/2/tweets"
            
            # Request payload
            payload = {
                "text": text
            }
            
            # Post the tweet
            response = oauth.post(
                url,
                json=payload
            )
            
            # Check if the request was successful
            if response.status_code in [200, 201]:
                response_data = response.json()
                tweet_id = response_data.get("data", {}).get("id")
                
                # Return success message with tweet ID
                yield self.create_json_message({
                    "status": "success",
                    "tweet_id": tweet_id,
                    "text": text,
                    "message": f"Tweet published successfully with ID: {tweet_id}"
                })
            else:
                error_message = f"Failed to post tweet. Status code: {response.status_code}, Response: {response.text}"
                yield self.create_text_message(error_message)
                
        except Exception as e:
            error_message = f"Error posting tweet: {str(e)}"
            yield self.create_text_message(error_message)