from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.videos import YoutubeVideosAnalyticsTool
from dify_plugin import ToolProvider


class YahooFinanceProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in YoutubeVideosAnalyticsTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={
                    "channel": "UC2JZCsZSOudXA08cMMRCL9g",
                    "start_date": "2020-01-01",
                    "end_date": "2024-12-31",
                }
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
