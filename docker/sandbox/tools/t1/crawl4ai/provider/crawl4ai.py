import requests
from typing import Any
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import ToolProvider


class Crawl4AIProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            server_url = credentials.get("server_url")
            api_token = credentials.get("api_token")
            
            # 验证URL格式
            if not server_url or not server_url.startswith("http"):
                raise ToolProviderCredentialValidationError("服务器URL无效，必须以http或https开头")
            
            # 简单的连接测试 - 尝试访问服务器根路径或健康检查端点
            try:
                # 先尝试访问根路径进行基本连接测试
                test_url = f"{server_url.rstrip('/')}"
                
                headers = {}
                if api_token:
                    headers["Authorization"] = f"Bearer {api_token}"
                
                response = requests.get(
                    test_url,
                    headers=headers,
                    timeout=5
                )
                
                # 只要能连接到服务器就认为验证成功
                # 不需要检查具体的响应内容
                if response.status_code >= 500:
                    raise ToolProviderCredentialValidationError(f"服务器内部错误，状态码：{response.status_code}")
                
            except requests.exceptions.ConnectionError:
                raise ToolProviderCredentialValidationError("无法连接到Crawl4AI服务器，请检查服务器URL是否正确")
            except requests.exceptions.Timeout:
                raise ToolProviderCredentialValidationError("连接Crawl4AI服务器超时，请检查网络连接")
            except requests.exceptions.RequestException as e:
                raise ToolProviderCredentialValidationError(f"连接到Crawl4AI服务器失败：{str(e)}")
                
        except Exception as e:
            if isinstance(e, ToolProviderCredentialValidationError):
                raise e
            raise ToolProviderCredentialValidationError(f"验证凭证时发生错误：{str(e)}")
