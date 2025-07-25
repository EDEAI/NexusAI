from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.wikipedia_search import WikiPediaSearchTool
from dify_plugin import ToolProvider


class WikiPediaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in WikiPediaSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "misaka mikoto"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
