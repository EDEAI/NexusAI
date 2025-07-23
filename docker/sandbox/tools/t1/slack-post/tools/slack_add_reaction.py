from typing import Any, Generator
import httpx
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class SlackAddReactionTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Add a reaction to a Slack message.
        API Document: https://api.slack.com/methods/reactions.add
        """
        bot_token = tool_parameters.get("bot_token", "").strip()
        if not bot_token:
            yield self.create_text_message("Invalid parameter: 'bot_token' is required.")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {bot_token}",
        }

        channel_id = tool_parameters.get("channel_id", "")
        if not channel_id:
            yield self.create_text_message("Invalid parameter: 'channel_id' is required.")
            return

        icon_name = tool_parameters.get("icon_name", "")
        if not icon_name:
            yield self.create_text_message("Invalid parameter: 'icon_name' is required.")
            return

        timestamp = tool_parameters.get("timestamp", "")
        if not timestamp:
            yield self.create_text_message("Invalid parameter: 'timestamp' is required.")
            return

        payload = {
            "channel": channel_id,
            "name": icon_name,
            "timestamp": timestamp,
        }

        try:
            res = httpx.post(
                "https://slack.com/api/reactions.add",
                headers=headers,
                json=payload,
            )

            if not res.is_success:
                yield self.create_text_message(
                    f"HTTP status code: {res.status_code}, response: {res.text}"
                )
                return

            data = res.json()
            if not data.get("ok", False):
                yield self.create_text_message(
                    f"Slack API error: {data.get('error', 'unknown_error')}"
                )
                return

        except Exception as e:
            yield self.create_text_message(f"Exception occurred: {str(e)}")
            return

        yield self.create_text_message("Reaction added successfully.")

