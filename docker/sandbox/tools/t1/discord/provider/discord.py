from typing import Any
from tools.discord_webhook import DiscordWebhookTool
from dify_plugin import ToolProvider


class DiscordProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        DiscordWebhookTool()
