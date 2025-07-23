from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.arxiv_search import ArxivSearchTool


class ArxivProvider(ToolProvider):
    def validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in ArxivSearchTool.from_credentials(credentials).invoke_from_executor(
                tool_parameters={"query": "test", "result_type": "link"},
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
