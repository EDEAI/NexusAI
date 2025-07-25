from typing import Any

from tools.exa_search import ExaSearchTool

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ExaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 使用ExaSearchTool来验证凭据
            tool = ExaSearchTool.from_credentials(credentials)
            for _ in tool.invoke(
                tool_parameters={"query": "test"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
