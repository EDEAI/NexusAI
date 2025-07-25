from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.pubmed_search import PubMedSearchTool
from dify_plugin import ToolProvider


class PubMedProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            PubMedSearchTool.from_credentials(credentials).invoke(tool_parameters={"query": "John Doe"})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
