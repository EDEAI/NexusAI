from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.translate import GoogleTranslate


class JsonExtractProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            GoogleTranslate().invoke(tool_parameters={"content": "这是一段测试文本", "dest": "en"})
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
