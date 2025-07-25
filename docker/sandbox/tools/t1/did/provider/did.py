from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.talks import TalksTool
from dify_plugin import ToolProvider


class DIDProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            TalksTool.from_credentials(credentials, user_id="").invoke(
                tool_parameters={
                    "source_url": "https://www.d-id.com/wp-content/uploads/2023/11/Hero-image-1.png",
                    "text_input": "Hello, welcome to use D-ID tool in Dify",
                }
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
