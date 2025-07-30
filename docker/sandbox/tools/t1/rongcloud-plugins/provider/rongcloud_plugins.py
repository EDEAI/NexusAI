"""
MIT License

Copyright (c) 2024 RongCloud Dify Plugin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import hashlib
import logging
import time
from typing import Dict, Any, Optional

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
import requests


logger = logging.getLogger(__name__)

# 版本号
RC_PLUGIN_VERSION = '0.1.1'

class RongCloudAPIToolProvider(ToolProvider):
    """融云 API 工具提供者类
    
    负责处理与融云 API 相关的所有操作，包括凭证验证、API 调用等。
    """
    
    # 版本号
    RC_PLUGIN_VERSION = RC_PLUGIN_VERSION
    
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """验证融云 API 凭证
        Args:
            credentials: 包含 host、app_key 和 app_secret 的字典
        Raises:
            ValueError: 当必需的凭证字段缺失时抛出
        """
        host = credentials["host"]
        app_key = credentials["app_key"]
        app_secret = credentials["app_secret"]

        if not host:
            raise ToolProviderCredentialValidationError("Missing required 'host'")
        if not app_key:
            raise ToolProviderCredentialValidationError("Missing required 'app_key'")
        if not app_secret:
            raise ToolProviderCredentialValidationError("Missing required 'app_secret'")
            
        try:
            self.check_auth(host, app_key, app_secret)
            logger.info("Credentials validated successfully")
        except Exception as e:
            logger.error(f"Error validating credentials: {str(e)}")
            raise ToolProviderCredentialValidationError(f"凭证验证失败: {e}")
        

    def check_auth(self, host: str, app_key: str, app_secret: str) -> None:
        """校验融云 API 凭证有效性
        Args:
            host: 融云 API Host
            app_key: AppKey
            app_secret: AppSecret
        Raises:
            Exception: 认证失败时抛出
        """
        data = {
            "userId": "testAuthUserId"
        }
        nonce = str(int(time.time()))
        timestamp = str(int(time.time() * 1000))
        signature = hashlib.sha1(f"{app_secret}{nonce}{timestamp}".encode()).hexdigest()
        headers = {
            "App-Key": app_key,
            "Nonce": nonce,
            "Timestamp": timestamp,
            "Signature": signature,
            "User-Agent": f'rc-dify-tool/{self.RC_PLUGIN_VERSION}'
        }
        response = requests.request(
            method="POST",
            url=f"{host}/user/info.json",
            headers=headers,
            data=data,
            timeout=10
        )
        if response.status_code != 200:
            error_msg = f"Authentication failed"
            raise Exception(error_msg)

