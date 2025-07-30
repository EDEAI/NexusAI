from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider
from dify_plugin.file.file import File, FileType

from tools.vectorizer import VectorizerTool

class VectorizerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            for _ in VectorizerTool.from_credentials(credentials).invoke(
                tool_parameters={
                    "mode": "test",
                    "image": File(
                        url="https://cloud.dify.ai/logo/logo-site.png",
                        mime_type="image/png",
                        filename="logo-site.png",
                        extension=".png",
                        type=FileType.IMAGE,
                    ),
                }
            ):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
