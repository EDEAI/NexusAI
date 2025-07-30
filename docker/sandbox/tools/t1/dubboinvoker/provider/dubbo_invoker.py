from typing import Any
import re

from dify_plugin import ToolProvider


class DubboInvokerProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """
        Validate Dubbo configuration credentials
        验证Dubbo配置凭据
        """
        # 验证Dubbo版本格式
        dubbo_version = credentials.get('dubbo_version', '2.4.10')
        if dubbo_version:
            # 检查版本格式是否合理 (例如: 2.4.10, 2.6.x, 2.7.x等)
            version_pattern = r'^\d+\.\d+(\.\d+|\.x)$'
            if not re.match(version_pattern, dubbo_version):
                raise ValueError(f"Invalid Dubbo version format: {dubbo_version}. Expected format like '2.4.10' or '2.6.x'")
        
        # 验证超时时间
        timeout = credentials.get('timeout', '60000')
        if timeout:
            try:
                timeout_value = int(timeout)
                if timeout_value <= 0:
                    raise ValueError("Timeout must be a positive integer")
                if timeout_value > 300000:  # 最大5分钟
                    raise ValueError("Timeout cannot exceed 300000ms (5 minutes)")
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid timeout value: {timeout}. Must be a positive integer in milliseconds")
                raise e 