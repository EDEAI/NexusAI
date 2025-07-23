from typing import Any, Generator
import httpx
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class DiscordWebhookTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Incoming Webhooks
        API Document:
            https://discord.com/developers/docs/resources/webhook#execute-webhook
        """
        content = tool_parameters.get("content", "")
        if not content:
            yield self.create_text_message("Invalid parameter content")
        webhook_url = tool_parameters.get("webhook_url", "")
        if not (
            webhook_url.startswith("https://discord.com/api/webhooks/")
            or webhook_url.startswith("https://discordapp.com/api/webhooks/")
        ):
            yield self.create_text_message(
                f"Invalid parameter webhook_url {webhook_url}, not a valid Discord webhook URL"
            )
        headers = {"Content-Type": "application/json"}
        payload = {
            "username": tool_parameters.get("username") or self.runtime.user_id,
            "content": content,
            "avatar_url": tool_parameters.get("avatar_url") or None,
        }
        try:
            res = httpx.post(webhook_url, headers=headers, json=payload)
            if res.is_success:
                yield self.create_text_message("Text message was sent successfully")
            else:
                yield self.create_text_message(
                    f"Failed to send the text message,                         status code: {res.status_code}, response: {res.text}"
                )
        except Exception as e:
            yield self.create_text_message(
                "Failed to send message through webhook. {}".format(e)
            )
