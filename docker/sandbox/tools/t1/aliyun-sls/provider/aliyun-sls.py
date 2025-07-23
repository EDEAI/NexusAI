from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from aliyun.log import LogClient


class AliyunSlsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 验证必要的凭证字段是否存在
            required_fields = ['endpoint', 'access_key_id', 'access_key_secret', 'project', 'logstore']
            for field in required_fields:
                if field not in credentials or not credentials[field]:
                    raise ValueError(f"缺少必要的凭证字段: {field}")
            
            # 尝试创建LogClient并验证连接
            endpoint = credentials['endpoint']
            access_key_id = credentials['access_key_id']
            access_key_secret = credentials['access_key_secret']
            project = credentials['project']
            logstore = credentials['logstore']
            
            # 创建LogClient实例
            client = LogClient(endpoint, access_key_id, access_key_secret)
            
            # 尝试获取项目信息以验证凭证是否有效
            client.get_logstore(project, logstore)

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
    
    def get_credentials_schema(self) -> dict:
        """返回凭证的JSON Schema定义"""
        return {
            "type": "object",
            "required": ["endpoint", "access_key_id", "access_key_secret", "project", "logstore"],
            "properties": {
                "endpoint": {
                    "type": "string",
                    "title": "Endpoint",
                    "description": "阿里云SLS服务的Endpoint，例如：cn-hangzhou.log.aliyuncs.com"
                },
                "access_key_id": {
                    "type": "string",
                    "title": "Access Key ID",
                    "description": "阿里云账号的Access Key ID"
                },
                "access_key_secret": {
                    "type": "string",
                    "title": "Access Key Secret",
                    "description": "阿里云账号的Access Key Secret",
                    "format": "password"
                },
                "project": {
                    "type": "string",
                    "title": "Project",
                    "description": "阿里云SLS的项目名称"
                },
                "logstore": {
                    "type": "string",
                    "title": "Logstore",
                    "description": "阿里云SLS的日志库名称"
                }
            }
        }
