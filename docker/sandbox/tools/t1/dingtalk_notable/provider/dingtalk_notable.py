from dify_plugin import ToolProvider
from dingtalk_api_utils import auth


class DingTalkSpreadsheetProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        auth(credentials)
