# from typing import Any

# from dify_plugin import ToolProvider
# from dify_plugin.errors.tool import ToolProviderCredentialValidationError


# class BaiduOcrProvider(ToolProvider):
#     def _validate_credentials(self, credentials: dict[str, Any]) -> None:
#         try:
#             """
#             IMPLEMENT YOUR VALIDATION HERE
#             """
#         except Exception as e:
#             raise ToolProviderCredentialValidationError(str(e))


from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from aip import AipOcr

class BaiduOCRProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            pass
            # 测试凭证有效性
            # client = AipOcr(
            #     credentials['app_id'],
            #     credentials['api_key'],
            #     credentials['secret_key']
            # )
            # 简单测试请求
            # client.basicGeneral('test')
        except Exception as e:
            raise ToolProviderCredentialValidationError(
                f"Invalid credentials: {str(e)}"
            )