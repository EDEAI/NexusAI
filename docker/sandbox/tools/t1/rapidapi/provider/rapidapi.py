from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.google_news import GooglenewsTool
from dify_plugin import ToolProvider


class RapidapiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in GooglenewsTool().fork_tool_runtime(meta={"credentials": credentials}).invoke(
                tool_parameters={"language_region": "en-US"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
