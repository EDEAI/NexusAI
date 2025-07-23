from tools.wecom_group_bot import WecomGroupBotTool
from dify_plugin import ToolProvider


class WecomProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        WecomGroupBotTool()
