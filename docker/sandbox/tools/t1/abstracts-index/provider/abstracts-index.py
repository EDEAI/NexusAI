from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from gradio_client import Client


class AbstractsIndexProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证 Gradio 端点连接
            gradio_endpoint = credentials.get("gradio_endpoint")
            if not gradio_endpoint:
                raise ToolProviderCredentialValidationError("Gradio endpoint is required")
            
            # 尝试连接到 Gradio 客户端
            client = Client(gradio_endpoint)
            
            # 可以尝试一个简单的查询来验证连接
            # 这里只是验证连接，不需要实际查询
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(f"Failed to connect to Gradio endpoint: {str(e)}")