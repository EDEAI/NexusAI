from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.searchStackExQuestions import SearchStackExQuestionsTool
from dify_plugin import ToolProvider


class StackExchangeProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            SearchStackExQuestionsTool.from_credentials(credentials).invoke(
                tool_parameters={
                    "intitle": "Test",
                    "sort": "relevance",
                    "order": "desc",
                    "site": "stackoverflow",
                    "accepted": True,
                    "pagesize": 1,
                }
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
