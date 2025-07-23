from typing import Any, Optional, Dict, List
from collections.abc import Generator
from contextlib import contextmanager
import requests
import json
import time
import logging

logger = logging.getLogger(__name__)

class MilvusBaseTool:
    """Milvus 工具基类，提供通用的 HTTP 连接和错误处理功能"""
    
    @contextmanager
    def _get_milvus_client(self, credentials: dict[str, Any]):
        """创建 Milvus HTTP 客户端的上下文管理器"""
        try:
            uri = credentials.get("uri")
            token = credentials.get("token")
            database = credentials.get("database", "default")
            
            if not uri:
                raise ValueError("URI is required")
            
            # 确保 URI 格式正确
            if not uri.startswith(("http://", "https://")):
                uri = f"http://{uri}"
            
            # 移除末尾的斜杠
            uri = uri.rstrip('/')
            
            # 创建 HTTP 客户端
            client = MilvusHttpClient(
                uri=uri,
                token=token if token else "",
                database=database,
                timeout=30.0
            )
            
            # 测试连接
            client.test_connection()
            
            logger.info(f"✅ [DEBUG] Successfully connected to Milvus HTTP API at {uri}")
            yield client
            
        except Exception as e:
            logger.error(f"❌ [DEBUG] Failed to connect to Milvus: {str(e)}")
            raise ValueError(f"Failed to connect to Milvus: {str(e)}")
    
    def _validate_collection_name(self, collection_name: str) -> bool:
        """验证集合名称"""
        if not collection_name or not isinstance(collection_name, str):
            return False
        if len(collection_name) > 255:
            return False
        # 集合名称只能包含字母、数字和下划线，且不能以数字开头
        import re
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', collection_name))
    
    def _parse_vector_data(self, data: str) -> list:
        """解析向量数据"""
        try:
            if isinstance(data, str):
                return json.loads(data)
            return data
        except (json.JSONDecodeError, TypeError):
            raise ValueError("Invalid vector data format. Expected JSON array.")
    
    def _parse_search_params(self, params_str: Optional[str]) -> dict:
        """解析搜索参数"""
        if not params_str:
            return {}
        
        try:
            return json.loads(params_str)
        except (json.JSONDecodeError, TypeError):
            return {}


class MilvusHttpClient:
    """Milvus HTTP 客户端类，封装 REST API 调用"""
    
    def __init__(self, uri: str, token: str = "", database: str = "default", timeout: float = 30.0):
        self.uri = uri
        self.token = token
        self.database = database
        self.timeout = timeout
        self.session = requests.Session()
        
        # 设置默认头部
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # 设置认证
        if token:
            self.session.headers['Authorization'] = f'Bearer {token}'
    
    def test_connection(self):
        """测试连接是否正常"""
        try:
            response = self._make_request('POST', '/v2/vectordb/collections/list', {})
            return response.get('code') == 0
        except Exception as e:
            raise ValueError(f"Connection test failed: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[dict] = None, max_retries: int = 3) -> dict:
        """发送 HTTP 请求"""
        url = f"{self.uri}{endpoint}"
        
        # 确保 data 包含 dbName
        if data is None:
            data = {}
        
        # 为所有请求添加数据库名称
        data['dbName'] = self.database
        
        logger.debug(f"🌐 [DEBUG] Making {method} request to: {url}")
        logger.debug(f"📦 [DEBUG] Request data: {data}")
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔄 [DEBUG] Attempt {attempt + 1}/{max_retries}")
                
                if method == 'GET':
                    response = self.session.get(url, headers=headers, timeout=self.timeout)
                elif method == 'POST':
                    response = self.session.post(url, json=data, headers=headers, timeout=self.timeout)
                elif method == 'PUT':
                    response = self.session.put(url, json=data, headers=headers, timeout=self.timeout)
                elif method == 'DELETE':
                    response = self.session.delete(url, headers=headers, timeout=self.timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                logger.debug(f"📡 [DEBUG] Response status: {response.status_code}")
                
                # 检查 HTTP 状态码
                if response.status_code != 200:
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    logger.error(f"❌ [DEBUG] Request failed: {error_msg}")
                    raise ValueError(error_msg)
                
                # 解析响应
                result = response.json()
                logger.debug(f"✅ [DEBUG] Response: {result}")
                
                # 检查 Milvus 响应码
                if result.get('code') != 0:
                    error_msg = result.get('message', 'Unknown error')
                    logger.error(f"❌ [DEBUG] Milvus API error: {error_msg}")
                    raise ValueError(f"Milvus API error: {error_msg}")
                
                return result
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ [DEBUG] Request attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Request failed after {max_retries} attempts: {str(e)}")
                
                # 指数退避
                time.sleep(2 ** attempt)
        
        # 这里不应该到达，但为了类型检查添加返回值
        raise ValueError("Request failed after all retries")
    
    # Collection 操作
    def list_collections(self) -> list:
        """列出所有集合"""
        response = self._make_request('POST', '/v2/vectordb/collections/list', {})
        return response.get('data', [])
    
    def has_collection(self, collection_name: str) -> bool:
        """检查集合是否存在"""
        try:
            response = self._make_request('POST', '/v2/vectordb/collections/describe', {
                'collectionName': collection_name
            })
            return response.get('code') == 0
        except:
            return False
    
    def create_collection(self, collection_name: str, dimension: int, metric_type: str = "COSINE", 
                         auto_id: bool = True, description: str = ""):
        """创建集合"""
        schema = {
            "autoID": auto_id,
            "fields": [
                {
                    "fieldName": "id",
                    "dataType": "Int64",
                    "isPrimary": True
                },
                {
                    "fieldName": "vector",
                    "dataType": "FloatVector",
                    "elementTypeParams": {
                        "dim": dimension
                    }
                }
            ]
        }
        
        index_params = [
            {
                "fieldName": "vector",
                "metricType": metric_type,
                "indexType": "AUTOINDEX"
            }
        ]
        
        data = {
            "collectionName": collection_name,
            "schema": schema,
            "indexParams": index_params
        }
        
        if description:
            data["description"] = description
        
        return self._make_request('POST', '/v2/vectordb/collections/create', data)
    
    def drop_collection(self, collection_name: str):
        """删除集合"""
        return self._make_request('POST', '/v2/vectordb/collections/drop', {
            'collectionName': collection_name
        })
    
    def describe_collection(self, collection_name: str):
        """描述集合"""
        response = self._make_request('POST', '/v2/vectordb/collections/describe', {
            'collectionName': collection_name
        })
        return response.get('data', {})
    
    def get_collection_stats(self, collection_name: str, timeout: Optional[float] = None) -> dict:
        """获取集合统计信息"""
        logger.debug(f"📊 [DEBUG] get_collection_stats() called for: {collection_name}")
        
        # 使用 describe 端点获取集合信息，因为 stats 端点不存在
        response = self._make_request('POST', '/v2/vectordb/collections/describe', {
            'collectionName': collection_name
        })
        
        collection_info = response.get('data', {})
        
        # 从 describe 响应中提取统计信息
        stats = {
            'collection_name': collection_info.get('collectionName', collection_name),
            'description': collection_info.get('description', ''),
            'num_shards': collection_info.get('shardsNum', 0),
            'num_partitions': collection_info.get('partitionsNum', 0),
            'num_fields': len(collection_info.get('fields', [])),
            'num_indexes': len(collection_info.get('indexes', [])),
            'consistency_level': collection_info.get('consistencyLevel', 'Unknown'),
            'load_state': collection_info.get('load', 'Unknown'),
            'auto_id': collection_info.get('autoId', False),
            'enable_dynamic_field': collection_info.get('enableDynamicField', False),
            'collection_id': collection_info.get('collectionID', 0),
            'fields': collection_info.get('fields', []),
            'indexes': collection_info.get('indexes', [])
        }
        
        logger.debug(f"📊 [DEBUG] Collection stats extracted from describe: {stats}")
        
        return stats
    
    def load_collection(self, collection_name: str):
        """加载集合"""
        return self._make_request('POST', '/v2/vectordb/collections/load', {
            'collectionName': collection_name
        })
    
    def release_collection(self, collection_name: str):
        """释放集合"""
        return self._make_request('POST', '/v2/vectordb/collections/release', {
            'collectionName': collection_name
        })
    
    # 数据操作
    def insert(self, collection_name: str, data: List[Dict[str, Any]], partition_name: Optional[str] = None):
        """插入数据"""
        request_data = {
            'collectionName': collection_name,
            'data': data
        }
        
        if partition_name:
            request_data['partitionName'] = partition_name
        
        return self._make_request('POST', '/v2/vectordb/entities/insert', request_data)
    
    def upsert(self, collection_name: str, data: list[dict[str, Any]], partition_name: Optional[str] = None):
        """插入或更新数据"""
        request_data: dict[str, Any] = {
            'collectionName': collection_name,
            'data': data
        }
        if partition_name:
            request_data['partitionName'] = partition_name
        return self._make_request('POST', '/v2/vectordb/entities/upsert', request_data)
    
    def search(
        self,
        collection_name: str,
        data: list[list[float]],
        anns_field: str = "vector",
        limit: int = 10,
        output_fields: Optional[list[str]] = None,
        filter: Optional[str] = None,
        search_params: Optional[dict] = None,
        partition_names: Optional[list[str]] = None,
        **kwargs
    ) -> list:
        """向量搜索"""
        payload: dict[str, Any] = {
            "collectionName": collection_name,
            "data": data,
            "annsField": anns_field,
            "limit": limit
        }

        # 添加可选参数
        if output_fields:
            payload["outputFields"] = output_fields
        if filter:
            payload["filter"] = filter
        if search_params:
            payload["searchParams"] = search_params
        if partition_names:
            payload["partitionNames"] = partition_names

        response = self._make_request(
            "POST", 
            "/v2/vectordb/entities/search", 
            payload
        )
        return response.get('data', [])
    
    def query(self, collection_name: str, filter: Optional[str] = None, output_fields: Optional[list[str]] = None,
              limit: Optional[int] = None, partition_names: Optional[list[str]] = None):
        """查询数据"""
        request_data: Dict[str, Any] = {
            'collectionName': collection_name
        }
        
        if filter:
            request_data['filter'] = filter
        
        if output_fields:
            request_data['outputFields'] = output_fields
        
        if limit is not None:
            request_data['limit'] = limit
        
        if partition_names:
            request_data['partitionNames'] = partition_names
        
        response = self._make_request('POST', '/v2/vectordb/entities/query', request_data)
        return response.get('data', [])
    
    def get(self, collection_name: str, ids: List[Any], output_fields: Optional[List[str]] = None,
            partition_names: Optional[List[str]] = None):
        """根据ID获取数据"""
        request_data: Dict[str, Any] = {
            'collectionName': collection_name,
            'id': ids
        }
        
        if output_fields:
            request_data['outputFields'] = output_fields
        
        if partition_names:
            request_data['partitionNames'] = partition_names
        
        response = self._make_request('POST', '/v2/vectordb/entities/get', request_data)
        return response.get('data', [])
    
    def delete(self, collection_name: str, ids: Optional[list[Any]] = None, filter: Optional[str] = None,
               partition_name: Optional[str] = None):
        """删除数据"""
        # 必须提供 ids (非空列表) 或 filter (非空字符串)
        has_valid_ids = isinstance(ids, list) and len(ids) > 0
        has_valid_filter = isinstance(filter, str) and len(filter.strip()) > 0

        if not has_valid_ids and not has_valid_filter:
            raise ValueError("Either a non-empty list of 'ids' or a non-empty 'filter' string must be provided for the delete operation.")

        request_data: dict[str, Any] = {
            'collectionName': collection_name
        }
        
        # 构建 filter 表达式
        if has_valid_ids and not has_valid_filter:
            # 根据ID类型（字符串或数字）构建 "in" 表达式
            if ids and all(isinstance(i, str) for i in ids):
                id_list_str = ", ".join(f'"{i}"' for i in ids)
            elif ids:
                id_list_str = ", ".join(str(i) for i in ids)
            else:
                id_list_str = ""
            request_data['filter'] = f"id in [{id_list_str}]"
        elif has_valid_filter:
            request_data['filter'] = filter
        
        # 如果同时有 ids 和 filter，优先使用 filter
        logger.debug(f"🗑️ [DEBUG] Delete operation with filter: {request_data.get('filter')}")

        if partition_name:
            request_data['partitionName'] = partition_name

        return self._make_request('POST', '/v2/vectordb/entities/delete', request_data)
    
    def close(self):
        """关闭连接"""
        self.session.close() 