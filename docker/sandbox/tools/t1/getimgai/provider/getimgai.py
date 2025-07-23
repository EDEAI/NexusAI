from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.text2image import Text2ImageTool
from dify_plugin import ToolProvider


class GetImgAIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            for _ in Text2ImageTool.from_credentials(credentials).invoke(
                tool_parameters={"prompt": "A fire egg", "response_format": "url", "style": "photorealism"}
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
