from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.stable_diffusion import StableDiffusionTool
from dify_plugin import ToolProvider


class StableDiffusionProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            instance = StableDiffusionTool.from_credentials(credentials)
            assert isinstance(instance, StableDiffusionTool)
            instance.validate_models()
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
