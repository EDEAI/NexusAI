from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.searchDevDocs import SearchDevDocsTool
from dify_plugin import ToolProvider


class DevDocsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in SearchDevDocsTool.from_credentials(credentials).invoke(
                tool_parameters={"doc": "python~3.12", "topic": "library/code"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
