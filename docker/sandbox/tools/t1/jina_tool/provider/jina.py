import json
from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from tools.jina_reader import JinaReaderTool


class JinaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if credentials["api_key"] is None:
                credentials["api_key"] = ""
            else:
                for result in JinaReaderTool.from_credentials(credentials).invoke(
                    tool_parameters={"url": "https://example.com"}
                ):
                    message = json.loads(result.message.text)
                if message["code"] != 200:
                    raise ToolProviderCredentialValidationError(message["message"])
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
