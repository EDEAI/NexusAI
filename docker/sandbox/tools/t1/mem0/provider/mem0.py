from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.retrieve_memory import RetrieveMem0Tool


class Mem0Provider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 使用RetrieveMem0Tool来验证凭据
            tool = RetrieveMem0Tool.from_credentials(credentials)
            for _ in tool.invoke(
                tool_parameters={"query": "test", "user_id": "validation_test"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
