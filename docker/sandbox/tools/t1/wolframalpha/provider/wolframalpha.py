from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.wolframalpha import WolframAlphaTool
from dify_plugin import ToolProvider


class GoogleProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in WolframAlphaTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"query": "1+2+....+111"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
