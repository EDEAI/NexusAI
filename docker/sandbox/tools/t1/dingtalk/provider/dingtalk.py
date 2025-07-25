from tools.dingtalk_group_bot import DingTalkGroupBotTool
from dify_plugin import ToolProvider


class DingTalkProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        DingTalkGroupBotTool()
        pass
