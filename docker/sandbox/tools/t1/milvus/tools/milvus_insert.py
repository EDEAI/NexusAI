from typing import Any, List, Dict
from collections.abc import Generator
import json
import logging
import re

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .milvus_base import MilvusBaseTool

logger = logging.getLogger(__name__)


class MilvusInsertTool(MilvusBaseTool, Tool):
    """Milvus 数据插入工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            collection_name = tool_parameters.get("collection_name")
            data = tool_parameters.get("data")
            
            if not collection_name:
                raise ValueError("Collection name is required")
            
            if not self._validate_collection_name(collection_name):
                raise ValueError("Invalid collection name format")
            
            if not data:
                raise ValueError("Data is required")
            
            logger.debug(f"🔍 [DEBUG] 接收到的数据类型: {type(data)}")
            if isinstance(data, str):
                logger.debug(f"🔍 [DEBUG] 数据预览: {data[:100]}...")
            
            # 解析数据
            parsed_data = self._parse_insert_data(data)
            
            with self._get_milvus_client(self.runtime.credentials) as client:
                # 检查集合是否存在
                if not client.has_collection(collection_name):
                    raise ValueError(f"Collection '{collection_name}' does not exist")
                
                result = self._perform_insert(client, collection_name, parsed_data, tool_parameters)
                yield from self._create_success_message(result)
                
        except Exception as e:
            logger.error(f"❌ [ERROR] 插入操作失败: {str(e)}")
            yield from self._handle_error(e)
    
    def _handle_error(self, error: Exception) -> Generator[ToolInvokeMessage]:
        """统一的错误处理"""
        error_msg = str(error)
        yield self.create_json_message({
            "success": False,
            "error": error_msg,
            "error_type": type(error).__name__
        })
    
    def _create_success_message(self, data: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """创建成功响应消息"""
        response = {
            "success": True,
            **data
        }
        yield self.create_json_message(response)
    
    def _parse_insert_data(self, data: str) -> List[Dict[str, Any]]:
        """解析插入数据"""
        try:
            logger.debug(f"🔄 [DEBUG] 开始解析数据")
            
            # 如果数据已经是列表，直接返回
            if isinstance(data, list):
                logger.debug("✅ [DEBUG] 数据已经是列表格式")
                return data
            
            # 如果数据是字符串，尝试解析
            if isinstance(data, str):
                # 尝试解析外层JSON
                try:
                    outer_json = json.loads(data)
                    
                    # 检查是否有data字段（嵌套JSON结构）
                    if isinstance(outer_json, dict) and 'data' in outer_json and isinstance(outer_json['data'], str):
                        logger.debug("🔍 [DEBUG] 检测到嵌套JSON结构，尝试解析内层数据")
                        inner_data = outer_json['data']
                        
                        # 尝试直接解析内层数据
                        try:
                            parsed_inner = json.loads(inner_data)
                            if isinstance(parsed_inner, list):
                                logger.debug("✅ [DEBUG] 成功直接解析内层数据")
                                return parsed_inner
                        except json.JSONDecodeError as e:
                            logger.debug(f"⚠️ [DEBUG] 直接解析内层数据失败: {str(e)}")
                            
                            # 尝试清理内层数据
                            try:
                                # 移除所有实际换行符，保留转义的\n
                                cleaned = re.sub(r'(?<!\\)\n', '', inner_data)
                                parsed_inner = json.loads(cleaned)
                                if isinstance(parsed_inner, list):
                                    logger.debug("✅ [DEBUG] 清理后成功解析内层数据")
                                    return parsed_inner
                            except json.JSONDecodeError:
                                logger.debug("⚠️ [DEBUG] 清理后解析内层数据失败，尝试更多方法")
                                
                                # 方法1: 处理转义问题
                                try:
                                    fixed_data = inner_data.replace('\\\\', '\\').replace('\\"', '"')
                                    parsed = json.loads(fixed_data)
                                    if isinstance(parsed, list):
                                        logger.debug("✅ [DEBUG] 方法1成功")
                                        return parsed
                                except:
                                    logger.debug("⚠️ [DEBUG] 方法1失败")
                                
                                # 方法2: 移除所有空白字符
                                try:
                                    compact_data = re.sub(r'\s+', '', inner_data)
                                    parsed = json.loads(compact_data)
                                    if isinstance(parsed, list):
                                        logger.debug("✅ [DEBUG] 方法2成功")
                                        return parsed
                                except:
                                    logger.debug("⚠️ [DEBUG] 方法2失败")
                                
                                # 方法3: 确保是JSON数组格式
                                try:
                                    if not inner_data.strip().startswith('['):
                                        inner_data = '[' + inner_data.strip()
                                    if not inner_data.strip().endswith(']'):
                                        inner_data = inner_data.strip() + ']'
                                    compact_data = re.sub(r'\s+', '', inner_data)
                                    parsed = json.loads(compact_data)
                                    if isinstance(parsed, list):
                                        logger.debug("✅ [DEBUG] 方法3成功")
                                        return parsed
                                except:
                                    logger.debug("⚠️ [DEBUG] 方法3失败")
                    
                    # 如果外层JSON是列表，直接返回
                    elif isinstance(outer_json, list):
                        logger.debug("✅ [DEBUG] 外层JSON已经是列表格式")
                        return outer_json
                    
                    # 其他情况
                    else:
                        raise ValueError("Data must be a list of entities or contain a 'data' field with a JSON array string")
                        
                except json.JSONDecodeError as e:
                    logger.debug(f"⚠️ [DEBUG] 解析外层JSON失败: {str(e)}")
                    
                    # 尝试直接解析为列表
                    if data.strip().startswith('[') and data.strip().endswith(']'):
                        try:
                            parsed = json.loads(data)
                            if isinstance(parsed, list):
                                logger.debug("✅ [DEBUG] 成功直接解析为列表")
                                return parsed
                        except:
                            logger.debug("⚠️ [DEBUG] 直接解析为列表失败")
            
            # 如果所有方法都失败，抛出异常
            raise ValueError("无法解析数据，所有方法都失败")
            
        except Exception as e:
            logger.error(f"❌ [ERROR] 解析数据时发生错误: {str(e)}")
            raise ValueError(f"Failed to parse data: {str(e)}")
    
    def _perform_insert(self, client, collection_name: str, data: List[Dict[str, Any]], params: dict[str, Any]) -> dict[str, Any]:
        """执行数据插入"""
        # 获取分区名称（可选）
        partition_name = params.get("partition_name")
        
        # 执行插入
        try:
            logger.debug(f"🔄 [DEBUG] 执行插入操作: 集合={collection_name}, 数据条数={len(data)}")
            
            # 验证数据结构
            for i, entity in enumerate(data):
                if not isinstance(entity, dict):
                    raise ValueError(f"Entity at index {i} must be a dictionary")
                
                if not entity:
                    raise ValueError(f"Entity at index {i} cannot be empty")
            
            result = client.insert(
                collection_name=collection_name,
                data=data,
                partition_name=partition_name
            )
            
            # 处理返回结果 - HTTP API 返回格式
            insert_count = len(data)  # HTTP API 不返回计数，用数据长度
            ids = result.get("data", {}).get("insertIds", []) if result else []
            
            logger.debug(f"✅ [DEBUG] 插入成功: 返回ID数量={len(ids)}")
            
            # 获取插入的向量维度信息（如果有向量字段）
            vector_info = self._analyze_vector_data(data)
            
            return {
                "operation": "insert",
                "collection_name": collection_name,
                "partition_name": partition_name,
                "insert_count": insert_count,
                "ids": ids,
                "vector_info": vector_info,
                "data_preview": data[:3] if len(data) > 3 else data  # 显示前3条数据预览
            }
            
        except Exception as e:
            logger.error(f"❌ [ERROR] 插入失败: {str(e)}")
            raise ValueError(f"Insert failed: {str(e)}")
    
    def _analyze_vector_data(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析向量数据信息"""
        vector_info = {
            "has_vector": False,
            "vector_fields": [],
            "dimensions": {}
        }
        
        if not data:
            return vector_info
        
        # 分析第一条数据来确定向量字段
        first_entity = data[0]
        
        for field_name, field_value in first_entity.items():
            if isinstance(field_value, list) and field_value:
                # 检查是否是数字列表（向量）
                if all(isinstance(x, (int, float)) for x in field_value):
                    vector_info["has_vector"] = True
                    vector_info["vector_fields"].append(field_name)
                    vector_info["dimensions"][field_name] = len(field_value)
        
        return vector_info 