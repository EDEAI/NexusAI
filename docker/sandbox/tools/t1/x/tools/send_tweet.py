import os
import json
from collections.abc import Generator
from typing import Any

import tweepy
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class SendTweetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Extract draft_id from parameters
        draft_id = tool_parameters.get("draft_id")
        
        if not draft_id:
            yield self.create_error_message("Draft ID is required")
            return
        
        # Get the draft file path
        draft_file_path = os.path.join("drafts", draft_id)
        
        # Check if draft exists
        if not os.path.exists(draft_file_path):
            yield self.create_error_message(f"Draft with ID {draft_id} does not exist")
            return
        
        try:
            # Read the draft
            with open(draft_file_path, "r") as f:
                draft = json.load(f)
            
            # Get tweet content
            content = draft.get("content")
            
            if not content:
                yield self.create_error_message("Invalid draft: No content found")
                return
            
            # Get credentials from tool provider
            credentials = self.credentials
            
            # Create Twitter client
            client = tweepy.Client(
                consumer_key=credentials["api_key"],
                consumer_secret=credentials["api_secret"],
                access_token=credentials["access_token"],
                access_token_secret=credentials["access_token_secret"]
            )
            
            # Send the tweet
            response = client.create_tweet(text=content)
            
            # Get the tweet ID
            tweet_id = response.data["id"]
            
            # Delete the draft after publishing
            os.remove(draft_file_path)
            
            # Return success message
            yield self.create_json_message({
                "status": "success",
                "tweet_id": tweet_id,
                "message": f"Tweet published successfully with ID: {tweet_id}"
            })
            
        except tweepy.TweepyException as e:
            yield self.create_error_message(f"Twitter API error: {str(e)}")
        except Exception as e:
            yield self.create_error_message(f"Error sending tweet: {str(e)}")