from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.image import StepfunTool
from dify_plugin import ToolProvider


class StepfunProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            StepfunTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={"prompt": "cute girl, blue eyes, white hair, anime style", "size": "256x256", "n": 1}
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
