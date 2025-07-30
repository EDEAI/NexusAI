from typing import Any, Dict, ClassVar
from threading import Lock
import logging
from confluent_kafka import Producer
import socket

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class KafkaConnectionManager:
    """Kafka连接管理器，支持多实例连接"""
    _instances: ClassVar[Dict[str, 'KafkaConnectionManager']] = {}
    _lock: ClassVar[Lock] = Lock()
    
    @classmethod
    def get_instance(cls, config: Dict[str, Any]) -> 'KafkaConnectionManager':
        """获取或创建实例，基于bootstrap.servers和认证信息作为唯一标识"""
        bootstrap_servers = config.get('bootstrap.servers', '')
        if not bootstrap_servers:
            raise ValueError("缺少必要的Kafka连接参数: bootstrap.servers")
        
        # 生成实例标识，包含bootstrap.servers和认证信息
        instance_key_parts = [bootstrap_servers]
        
        # 如果存在安全协议相关配置，也加入到实例标识中
        for key in ['security.protocol', 'sasl.mechanism', 'sasl.username']:
            if key in config:
                instance_key_parts.append(f"{key}={config[key]}")
        
        instance_key = "|".join(instance_key_parts)
        
        with cls._lock:
            if instance_key not in cls._instances:
                cls._instances[instance_key] = cls(config, instance_key)
            return cls._instances[instance_key]
    
    def __init__(self, config: Dict[str, Any], instance_key: str) -> None:
        """初始化实例"""
        self._config = config
        self._producer = None
        self._lock = Lock()
        self._instance_key = instance_key
        self._bootstrap_servers = config.get('bootstrap.servers', '')
        
        # 记录安全协议信息
        self._security_protocol = config.get('security.protocol', 'PLAINTEXT')
        self._sasl_mechanism = config.get('sasl.mechanism', "PLAIN")
        self._sasl_username = config.get('sasl.username', "")
        self._sasl_password = config.get('sasl.password', "")
        self._has_sasl = self._sasl_username and self._sasl_password
        
        # 日志记录初始化信息
        security_info = f", 安全协议: {self._security_protocol}"
        if self._has_sasl:
            security_info += f", SASL机制: {self._sasl_mechanism}, 用户名: {self._sasl_username}"
        else:
            del self._config['security.protocol']
            del self._config['sasl.username']
            del self._config['sasl.password']
            del self._config['sasl.mechanism']

        # 设置client.id
        self._config['client.id'] = self._config.get('client.id', 'dify-kafka-plugin-' + socket.gethostname())

        logging.info(f"初始化Kafka连接管理器，服务器: {self._bootstrap_servers}{security_info}")
    
    def get_producer(self) -> Producer:
        """获取Kafka Producer实例，如果不存在则创建"""
        with self._lock:
            if self._producer is None:
                try:
                    self._producer = Producer(self._config)
                    
                    # 构建日志信息，包含身份验证信息
                    log_msg = f"Kafka Producer已创建，服务器: {self._bootstrap_servers}"
                    if self._has_sasl:
                        log_msg += f", 使用SASL认证({self._sasl_mechanism})"
                    
                    logging.info(log_msg)
                except Exception as e:
                    logging.error(f"创建Kafka Producer失败: {str(e)}")
                    raise RuntimeError(f"创建Kafka Producer失败: {str(e)}")
            
            return self._producer
    
    def reset_connection(self) -> None:
        """重置Kafka连接"""
        with self._lock:
            if self._producer is not None:
                # 使用confluent-kafka的方式关闭连接
                self._producer.flush()
                self._producer = None
                logging.info(f"Kafka Producer已重置，服务器: {self._bootstrap_servers}")
    
    @classmethod
    def close_all_connections(cls) -> None:
        """关闭所有Kafka连接"""
        with cls._lock:
            for key, instance in cls._instances.items():
                try:
                    instance.reset_connection()
                    logging.info(f"关闭Kafka连接，实例: {key}")
                except Exception as e:
                    logging.error(f"关闭Kafka连接失败，实例: {key}, 错误: {str(e)}")
            cls._instances.clear()


class KafkaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            # 检查必要的连接参数
            required_params = ['bootstrap.servers']
            for param in required_params:
                if param not in credentials:
                    raise ValueError(f"缺少必要的Kafka连接参数: {param}")

            username = credentials.get('sasl.username', '')
            password = credentials.get('sasl.password', '')
            security_protocol = credentials.get('security.protocol', 'PLAINTEXT')
            
            # 检查SASL认证配置的一致性
            if username and password:
                # 检查安全协议配置
                if not security_protocol.startswith('SASL_'):
                    logging.warning(f"检测到SASL认证信息，但安全协议设置为{security_protocol}，已自动调整为SASL_SSL")
                    # 自动调整安全协议
                    credentials['security.protocol'] = 'SASL_SSL'
                
                # 检查SASL机制
                if 'sasl.mechanism' not in credentials:
                    logging.warning("未指定SASL机制，默认使用PLAIN")
                    credentials['sasl.mechanism'] = 'PLAIN'

            else:
                del credentials['security.protocol']
                del credentials['sasl.username']
                del credentials['sasl.password']
                del credentials['sasl.mechanism']
            
            # 创建临时Producer进行连接测试
            producer = Producer(credentials)
            
            # 执行一个简单的元数据请求来验证连接
            # 设置超时时间为5秒
            metadata = producer.list_topics(timeout=5)
            
            # 关闭测试连接
            producer.flush()

            logging.info("Kafka连接测试成功")
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
