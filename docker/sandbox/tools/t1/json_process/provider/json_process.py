from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.parse import JSONParseTool


class JsonExtractProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            JSONParseTool().invoke(
                tool_parameters={"content": '{"name": "John", "age": 30, "city": "New York"}', "json_filter": "$.name"},
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
