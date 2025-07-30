from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from mattermostautodriver import Driver


class BotAccounts(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        message_type = tool_parameters["message_type"]
        mattermost_domain = tool_parameters["mattermost_domain"]
        mattermost_port = tool_parameters["mattermost_port"]
        bot_access_token = tool_parameters["bot_access_token"]
        channel_id = tool_parameters["channel_id"]
        user_id = tool_parameters["user_id"]
        message = tool_parameters["message"]
        driver = Driver(
            {
                "url": mattermost_domain,
                "port": mattermost_port,
                "token": bot_access_token,
            }
        )
        driver.login()
        if message_type == "normal":
            mattermost_reply = {"channel_id": channel_id, "message": message}
            driver.posts.create_post(mattermost_reply)
        else:
            mattermost_reply = {
                "user_id": user_id,
                "post": {"channel_id": channel_id, "message": message},
            }
            driver.posts.create_post_ephemeral(mattermost_reply)
        yield self.create_text_message(message)
