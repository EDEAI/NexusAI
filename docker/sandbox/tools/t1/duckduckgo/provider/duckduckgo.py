from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.ddgo_search import DuckDuckGoSearchTool
from dify_plugin import ToolProvider


class DuckDuckGoProvider(ToolProvider):
    def validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in DuckDuckGoSearchTool.from_credentials(
                credentials
            ).invoke_from_executor(
                tool_parameters={
                    "query": "test",
                    "max_results": 5,
                },
            ):
                pass

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
