from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider

from tools.translate import BaiduTranslateTool


class BaiduTranslateProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in BaiduTranslateTool.from_credentials(credentials).invoke(
                tool_parameters={"q": "这是一段测试文本", "from": "auto", "to": "en"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
