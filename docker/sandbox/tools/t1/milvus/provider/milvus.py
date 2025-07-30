from typing import Any
import requests
import time

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class MilvusProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """验证 Milvus 连接凭据"""
        try:
            # 获取连接参数
            uri = credentials.get("uri")
            token = credentials.get("token")
            database = credentials.get("database", "default")
            
            if not uri:
                raise ToolProviderCredentialValidationError("URI is required")
            
            # 确保 URI 格式正确
            if not uri.startswith(("http://", "https://")):
                uri = f"http://{uri}"
            
            # 移除末尾的斜杠
            uri = uri.rstrip('/')
            
            # 创建 HTTP 会话
            session = requests.Session()
            session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
            
            # 设置认证
            if token:
                session.headers['Authorization'] = f'Bearer {token}'
            
            # 测试连接 - 尝试列出集合
            test_url = f"{uri}/v2/vectordb/collections/list"
            
            try:
                response = session.post(test_url, json={}, timeout=10.0)
                
                # 检查 HTTP 状态码
                if response.status_code != 200:
                    raise ToolProviderCredentialValidationError(
                        f"HTTP {response.status_code}: {response.text}"
                    )
                
                # 解析响应
                result = response.json()
                
                # 检查 Milvus 响应码
                if result.get('code') != 0:
                    error_msg = result.get('message', 'Unknown error')
                    raise ToolProviderCredentialValidationError(
                        f"Milvus API error: {error_msg}"
                    )
                
                # 验证成功
                
            except requests.exceptions.RequestException as e:
                raise ToolProviderCredentialValidationError(
                    f"Failed to connect to Milvus: {str(e)}"
                )
            finally:
                session.close()
                
        except ToolProviderCredentialValidationError:
            raise
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
