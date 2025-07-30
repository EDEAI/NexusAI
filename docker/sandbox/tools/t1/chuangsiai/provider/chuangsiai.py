from typing import Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from chuangsiai_sdk import ChuangsiaiClient

class ChuangsiaiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证提供的 创思 AccessKey 是否有效。
        尝试使用该 token 创建一个测试页面。
        如果验证失败，应抛出 ToolProviderCredentialValidationError 异常。
        """
        access_key = credentials.get("chuangsi_access_key")
        secret_key = credentials.get("chuangsi_secret_key")
        if not access_key:
            # raise ToolProviderCredentialValidationError("创思 AccessKey 不能为空。")
            raise ToolProviderCredentialValidationError("AccessKey cannot be empty.")
        if not secret_key:
            # raise ToolProviderCredentialValidationError("创思 SecretKey 不能为空。")
            raise ToolProviderCredentialValidationError("SecretKey cannot be empty.")

        try:
            # 尝试执行一个凭证验证
            # 1. 初始化签名工具
            headers={ "X-Referer":"dify" }
            client = ChuangsiaiClient(access_key=access_key,secret_key=secret_key,headers=headers)
            # 2. 调用 验证API
            data =  client.verify()
            # print("验证:", response_data)
            if data.get("code") == 200:
                print("✅ 验证成功:", data)
                return
            else:
                print("❌ 验证错误:", data)
                raise Exception(data.get("message", "chuangsiai Voucher verification failed, unknown error."))
        except Exception as e:
            print("❌ 验证请求错误:", e)
            # 如果 API 调用失败，说明凭证很可能无效
            raise ToolProviderCredentialValidationError(f"chuangsiai Voucher verification failed: {e}")