from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.query_doi import CrossRefQueryDOITool
from dify_plugin import ToolProvider


class CrossRefProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in CrossRefQueryDOITool.from_credentials(credentials).invoke(
                tool_parameters={"doi": "10.1007/s00894-022-05373-8"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
