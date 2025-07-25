from typing import Dict, Any
from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from storage.storage import Storage, RedisStorage

class SafetyChatProvider(ToolProvider):
    """安全聊天插件提供者
    
    整合访问频率限制、外部用户认证功能。
    """
    
    def __init__(self):
        super().__init__()
        
    def _validate_credentials(self, credentials: Dict[str, Any]) -> None:
        """验证凭证
        
        验证所有子功能所需的凭证。
        
        Args:
            credentials: 凭证信息
            
        Raises:
            ToolProviderCredentialValidationError: 凭证验证失败
        """
        try:
            # 验证存储类型
            storage_type = credentials.get(Storage.STORAGE_TYPE_KEY, Storage.PLUGIN_STORAGE_TYPE)
            if storage_type not in [Storage.REDIS_STORAGE_TYPE, Storage.PLUGIN_STORAGE_TYPE]:
                raise ToolProviderCredentialValidationError(f"Unsupported storage type: {storage_type}")
                
            # 如果使用Redis，验证Redis配置
            if storage_type == Storage.REDIS_STORAGE_TYPE:
                if not credentials.get(Storage.REDIS_HOST_KEY):
                    raise ToolProviderCredentialValidationError("Redis host is required")
                if not credentials.get(Storage.REDIS_PORT_KEY):
                    raise ToolProviderCredentialValidationError("Redis port is required")
                
                # 使用 RedisStorage 测试连接
                try:
                    storage = RedisStorage(
                        redis_host=credentials[Storage.REDIS_HOST_KEY],
                        redis_port=int(credentials[Storage.REDIS_PORT_KEY]),
                        redis_password=credentials.get(Storage.REDIS_PASSWORD_KEY),
                        redis_db=credentials.get(Storage.REDIS_DB_KEY, 0)
                    )
                    # 测试连接 - 尝试获取一个不存在的键来验证连接
                    test_key = "safety_chat:connection_test"
                    storage.get(test_key)
                except Exception as e:
                    raise ToolProviderCredentialValidationError(f"Redis connection failed: {str(e)}")
            
        except Exception as e:
            if isinstance(e, ToolProviderCredentialValidationError):
                raise e
            raise ToolProviderCredentialValidationError(str(e)) 