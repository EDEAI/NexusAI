from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests
from requests.packages import urllib3

class PrometheusProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证必要的凭证字段是否存在
            if "api_url" not in credentials:
                raise ValueError("Prometheus API URL is required")
            
            # 尝试连接Prometheus服务器
            api_url = credentials["api_url"]
            headers = {}
            
            # 如果提供了认证信息，则添加到请求头中
            if "username" in credentials and "password" in credentials:
                import base64
                auth_str = f"{credentials['username']}:{credentials['password']}"
                auth_bytes = auth_str.encode('ascii')
                base64_bytes = base64.b64encode(auth_bytes)
                base64_auth = base64_bytes.decode('ascii')
                headers["Authorization"] = f"Basic {base64_auth}"
            
            # 如果提供了令牌，则添加到请求头中
            if "token" in credentials:
                headers["Authorization"] = f"Bearer {credentials['token']}"
            
            # 测试连接
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(
                f"{api_url}/api/v1/query", 
                params={"query": "up","limit": 1},
                headers=headers,
                verify=False,
                timeout=5
            )
            
            # 检查响应
            if response.status_code != 200:
                raise ValueError(f"cannot connect to Prometheus server: HTTP {response.status_code}")
            
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
