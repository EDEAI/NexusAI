from typing import Any
import requests
import uuid
import json
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.ai_guardrails import AiGuardrailsTool

SERVICE_URL = "https://green-cip.cn-shanghai.aliyuncs.com"

class AiGuardrailsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        验证提供的 AccessKey ID 和 AccessKey Secret 是否有效。
        如果验证失败，应抛出 ToolProviderCredentialValidationError 异常。
        """
        aliyun_access_key = credentials.get("aliyun_access_key")
        aliyun_access_secret = credentials.get("aliyun_access_secret")
        if not aliyun_access_key:
            raise ToolProviderCredentialValidationError("阿里云 AccessKey ID 不能为空。")
        if not aliyun_access_secret:
            raise ToolProviderCredentialValidationError("阿里云 AccessKey Secret 不能为空。")

        try:
            AiGuardrailsTool.from_credentials(credentials).invoke(tool_parameters={"content": "这是一条测试数据", "type": "input"})
        except Exception as e:
            # 如果 API 调用失败，说明凭证很可能无效
            raise ToolProviderCredentialValidationError(f"阿里云AccessKey验证失败: {e}")
