from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.web_search import WebSearchTool
from dify_plugin import ToolProvider


class WebSearchAPIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in WebSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "what is llm"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
