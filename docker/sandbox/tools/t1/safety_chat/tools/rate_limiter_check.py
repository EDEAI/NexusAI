from typing import Any, Generator, Dict
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base.rate_limiter_base import RateLimiterMixin
from storage.storage import Storage, RedisStorage, PluginPersistentStorage
from utils.rate_limiter_algorithms import RateLimiterAlgorithm

class RateLimiterCheckTool(Tool, RateLimiterMixin):
    """访问频率限制检查工具
    
    检查用户的访问频率是否超出限制。
    支持基于用户ID和动作类型的多维度限流。
    """
    
    def __init__(self, runtime, session):
        """初始化工具
        
        Args:
            runtime: 运行时环境
            session: 会话信息
        """
        Tool.__init__(self, runtime=runtime, session=session)
        RateLimiterMixin.__init__(self, runtime=runtime, session=session)
        self.algorithm = None
        # 使用插件持久化存储
        self.storage = PluginPersistentStorage(self.session.storage)
         
    def validate_parameters(self, parameters: Dict[str, Any], required_fields: list = None) -> None:
        """验证参数
        
        Args:
            parameters: 参数字典
            required_fields: 必需字段列表
            
        Raises:
            ValueError: 参数验证失败
        """
        if required_fields is None:
            required_fields = [RateLimiterAlgorithm.USER_ID_KEY, RateLimiterAlgorithm.ACTION_TYPE_KEY]
            
        for field in required_fields:
            if not parameters.get(field):
                raise ValueError(f"Missing required parameter: {field}")
                
        if RateLimiterAlgorithm.ALGORITHM_TYPE_KEY in parameters and parameters[RateLimiterAlgorithm.ALGORITHM_TYPE_KEY] not in self.ALGORITHM_MAP:
            raise ValueError("Unsupported algorithm type")
            
    def _invoke(self, parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行工具调用
        
        Args:
            parameters: 工具参数
            
        Yields:
            ToolInvokeMessage: 调用结果
        """
        try:
            # 验证参数
            self.validate_parameters(parameters)
            
            # 初始化存储
            self.init_storage()
                
            # 获取频率限制配置
            config_unique_id = parameters.get(RateLimiterAlgorithm.UNIQUE_ID_KEY)
            # 如果配置不存在, 则根据 parameters 初始化配置
            self.init_config(config_unique_id, parameters)

            # 初始化算法
            self.algorithm = self.get_algorithm(
                algorithm_type=parameters.get(RateLimiterAlgorithm.ALGORITHM_TYPE_KEY),
                **{k: v for k, v in parameters.items() if k != RateLimiterAlgorithm.ALGORITHM_TYPE_KEY}
            )
            
            # 执行限流检查
            key = f"{parameters[RateLimiterAlgorithm.USER_ID_KEY]}:{parameters[RateLimiterAlgorithm.ACTION_TYPE_KEY]}:{config_unique_id}"
            result = self.algorithm.check(key)
            
            # 返回结果
            yield self.create_variable_message(RateLimiterAlgorithm.ALLOWED_KEY, result[RateLimiterAlgorithm.ALLOWED_KEY])
            yield self.create_variable_message(RateLimiterAlgorithm.REMAINING_KEY, result[RateLimiterAlgorithm.REMAINING_KEY])
            yield self.create_variable_message(RateLimiterAlgorithm.RESET_TIME_KEY, result[RateLimiterAlgorithm.RESET_TIME_KEY])
            yield self.create_variable_message(RateLimiterAlgorithm.REASON_KEY, result[RateLimiterAlgorithm.REASON_KEY])
            yield self.create_variable_message(RateLimiterAlgorithm.REASON_CN_KEY, result[RateLimiterAlgorithm.REASON_CN_KEY])
            yield self.create_variable_message(RateLimiterAlgorithm.REASON_CODE_KEY, result[RateLimiterAlgorithm.REASON_CODE_KEY])
            
        except Exception as e:
            yield self.create_text_message(f"Execution failed: {str(e)}")