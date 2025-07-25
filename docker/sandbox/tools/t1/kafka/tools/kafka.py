from collections.abc import Generator
from typing import Any, Dict
import socket
import logging
import time
from confluent_kafka import KafkaException
import copy
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from provider.kafka import KafkaConnectionManager
from dify_plugin.errors.model import InvokeServerUnavailableError

message_default_headers = {
          "X-Dify-Plugin-Name": "kafka",
          "X-Dify-Plugin-IP": socket.gethostbyname(socket.gethostname()),
          "X-Dify-Plugin-Hostname": socket.gethostname(),
}

class KafkaTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 从工具参数中获取必要的参数
        topic = tool_parameters.get('topic')
        message = tool_parameters.get('message')
        key = tool_parameters.get('key')
        
        # 获取可能的自定义连接参数
        custom_bootstrap_servers = tool_parameters.get('bootstrap_servers')
        custom_security_protocol = tool_parameters.get('security_protocol')
        custom_sasl_mechanism = tool_parameters.get('sasl_mechanism')
        custom_sasl_username = tool_parameters.get('sasl_username')
        custom_sasl_password = tool_parameters.get('sasl_password')
        
        if not topic:
            yield self.create_text_message("错误: 未提供Kafka主题名称")
            raise InvokeServerUnavailableError("未提供Kafka主题名称")
        
        if not message:
            yield self.create_text_message("错误: 未提供消息内容")
            raise InvokeServerUnavailableError("未提供消息内容")
        
        # 从凭证中获取Kafka配置
        credentials = copy.deepcopy(self.runtime.credentials)
      
        # 标记是否进行了自定义配置
        has_custom_config = False
        
        # 如果提供了自定义参数，则覆盖凭证中的配置
        if custom_bootstrap_servers:
            has_custom_config = True
            original_servers = credentials.get('bootstrap.servers', '未配置')
            credentials['bootstrap.servers'] = custom_bootstrap_servers
            logging.info(f"使用自定义Kafka服务器: {custom_bootstrap_servers}, 原服务器: {original_servers}")
        
        # 处理自定义安全协议
        if custom_security_protocol:
            has_custom_config = True
            original_protocol = credentials.get('security.protocol', 'PLAINTEXT')
            credentials['security.protocol'] = custom_security_protocol
            logging.info(f"使用自定义安全协议: {custom_security_protocol}, 原协议: {original_protocol}")
        
        # 处理自定义SASL机制
        if custom_sasl_mechanism:
            has_custom_config = True
            original_mechanism = credentials.get('sasl.mechanism', 'PLAIN')
            credentials['sasl.mechanism'] = custom_sasl_mechanism
            logging.info(f"使用自定义SASL机制: {custom_sasl_mechanism}, 原机制: {original_mechanism}")
        
        # 处理SASL用户名和密码
        if custom_sasl_username and custom_sasl_password:
            has_custom_config = True
            original_username = credentials.get('sasl.username', '未配置')
            credentials['sasl.username'] = custom_sasl_username
            credentials['sasl.password'] = custom_sasl_password
            
            # 如果设置了SASL凭证但未设置安全协议，则自动设置为SASL_SSL
            if 'security.protocol' not in credentials or not credentials['security.protocol'].startswith('SASL_'):
                original_protocol = credentials.get('security.protocol', 'PLAINTEXT')
                credentials['security.protocol'] = 'SASL_SSL'
                logging.info(f"检测到SASL认证信息，但安全协议设置为{original_protocol}，已自动调整为SASL_SSL")
            
            # 如果未设置SASL机制，则默认使用PLAIN
            if 'sasl.mechanism' not in credentials:
                credentials['sasl.mechanism'] = 'PLAIN'
                logging.info("未指定SASL机制，默认使用PLAIN")
            
            logging.info(f"使用自定义SASL凭证，用户名: {custom_sasl_username}, 原用户名: {original_username}")
        elif custom_sasl_username or custom_sasl_password:
            # 如果只提供了一个，则报错
            error_msg = "错误: SASL用户名和密码必须同时提供"
            logging.error(error_msg)
            raise InvokeServerUnavailableError(error_msg)
        
        bootstrap_servers = credentials.get('bootstrap.servers', '')
        security_protocol = credentials.get('security.protocol', 'PLAINTEXT')

        username = credentials.get('sasl.username', '')
        password = credentials.get('sasl.password', '')
        sasl_mechanism = credentials.get('sasl.mechanism', '')
        
        # 确定是否使用SASL认证
        has_sasl = username and password
        
        # 如果进行了自定义配置，输出完整的配置日志（不包含密码）
        if has_custom_config:
            log_parts = []
            # 添加服务器信息
            log_parts.append(f"服务器: {bootstrap_servers}")
            
            # 添加安全协议信息
            if security_protocol:
                log_parts.append(f"安全协议: {security_protocol}")
            
            # 添加SASL信息（如果有）
            if has_sasl:
                log_parts.append(f"SASL机制: {sasl_mechanism}")
                log_parts.append(f"SASL用户名: {username}")
            
            logging.info(f"最终Kafka配置: {', '.join(log_parts)}")
        
        try:
            # 根据当前凭证获取对应的Kafka连接实例
            kafka_manager = KafkaConnectionManager.get_instance(credentials)
            producer = kafka_manager.get_producer()
            
            # 准备消息发送的回调函数
            delivery_results: Dict[str, Any] = {'success': False, 'error': None, 'offset': None, 'partition': None}
            
            def delivery_callback(err, msg):
                if err is not None:
                    delivery_results['error'] = str(err)
                else:
                    delivery_results['success'] = True
                    delivery_results['offset'] = msg.offset()
                    delivery_results['partition'] = msg.partition()
                    delivery_results['topic'] = msg.topic()
            
            headers = message_default_headers

            # 发送消息
            producer.produce(
                topic=topic,
                value=message.encode('utf-8'),
                headers=headers,
                key=key.encode('utf-8') if key else None,
                callback=delivery_callback
            )
            
            # 立即刷新一次，确保消息发送出去
            producer.flush(timeout=10)  # 10秒超时
            
            # 等待回调结果
            max_wait_time = 5  # 最多等待5秒
            start_time = time.time()
            
            while not delivery_results['success'] and delivery_results['error'] is None:
                if time.time() - start_time > max_wait_time:
                    break
                producer.poll(0.1)  # 轮询事件，触发回调
            
            # 返回结果
            if delivery_results['success']:
                result = {
                    "status": "success",
                    "topic": topic,
                    "message": message,
                    "partition": delivery_results['partition'],
                    "offset": delivery_results['offset'],
                    "bootstrap_servers": bootstrap_servers
                }
                if key:
                    result["key"] = key
                
                # 如果使用了SASL认证，在结果中包含认证信息（不包含敏感信息）
                if has_sasl:
                    result["security"] = {
                        "protocol": security_protocol,
                        "mechanism": sasl_mechanism,
                        "username": username
                    }
                
                yield self.create_json_message(result)
                yield self.create_text_message(f"消息发送成功，主题: {topic}, 分区: {delivery_results['partition']}, 偏移量: {delivery_results['offset']}")
            else:
                error_message = delivery_results['error'] if delivery_results['error'] else "消息发送超时或未收到确认"
                raise InvokeServerUnavailableError(f"错误: 消息发送失败 - {error_message} (服务器: {bootstrap_servers})")
        
        except KafkaException as ke:
            # 处理Kafka异常
            error_message = f"Kafka错误: {str(ke)} (服务器: {bootstrap_servers})"
            logging.error(error_message)
            yield self.create_text_message(error_message)
            
            # 尝试重置连接
            try:
                # 获取实例并重置连接
                kafka_manager = KafkaConnectionManager.get_instance(credentials)
                kafka_manager.reset_connection()
            except Exception as reset_error:
                logging.error(f"重置Kafka连接失败: {str(reset_error)}")
                raise InvokeServerUnavailableError(f"连接失败: {str(reset_error)}")
        except Exception as e:
            # 处理其他异常
            error_message = f"发送消息时发生错误: {str(e)} (服务器: {bootstrap_servers})"
            logging.error(error_message)
            raise InvokeServerUnavailableError(error_message)
