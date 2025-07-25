from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.serper_search import SerperSearchTool
from dify_plugin import ToolProvider


class SerperProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in SerperSearchTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "test", "result_type": "link"}
            ): 
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
