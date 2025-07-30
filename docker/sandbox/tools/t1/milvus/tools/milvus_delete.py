from typing import Any, List, Union
from collections.abc import Generator
import json
import ast
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .milvus_base import MilvusBaseTool

logger = logging.getLogger(__name__)

class MilvusDeleteTool(MilvusBaseTool, Tool):
    """Milvus 数据删除工具"""
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行删除操作"""
        try:
            collection_name = tool_parameters.get("collection_name")
            ids_param = tool_parameters.get("ids")
            filter_expr = tool_parameters.get("filter")
            partition_name = tool_parameters.get("partition_name", "")

            if not collection_name or not self._validate_collection_name(collection_name):
                raise ValueError("Invalid or missing collection name.")

            logger.debug(f"🔍 [DEBUG] Delete parameters - collection: {collection_name}, ids: {ids_param}, filter: {filter_expr}")
            
            # 处理 ids 参数
            ids = None
            if ids_param:
                ids = self._parse_ids(ids_param)
                logger.debug(f"🔢 [DEBUG] Parsed IDs: {ids}")
                
            # 校验 ids 和 filter
            if not ids and not filter_expr:
                raise ValueError("Either 'ids' or 'filter' must be provided for the delete operation.")

            with self._get_milvus_client(self.runtime.credentials) as client:
                if not client.has_collection(collection_name):
                    raise ValueError(f"Collection '{collection_name}' does not exist.")
                
                # 执行删除
                result = client.delete(
                    collection_name=collection_name,
                    ids=ids,
                    filter=filter_expr,
                    partition_name=partition_name if partition_name else None
                )
                
                response_data = {
                    "operation": "delete",
                    "collection_name": collection_name,
                    "success": True,
                    "message": f"Delete operation was successful for collection '{collection_name}'."
                }
                yield from self._create_success_message(response_data)
                
        except Exception as e:
            logger.error(f"❌ [DEBUG] Delete operation failed: {str(e)}")
            yield from self._handle_error(e)

    def _parse_ids(self, ids_param: Union[str, List]) -> List:
        """安全地解析 IDs 参数"""
        if isinstance(ids_param, list):
            return ids_param
        
        if isinstance(ids_param, str):
            try:
                # 尝试使用 json.loads 解析
                try:
                    parsed_ids = json.loads(ids_param)
                    if isinstance(parsed_ids, list):
                        return parsed_ids
                except json.JSONDecodeError:
                    # 如果 JSON 解析失败，尝试使用 ast.literal_eval
                    parsed_ids = ast.literal_eval(ids_param)
                    if isinstance(parsed_ids, list):
                        return parsed_ids
                    
                # 如果解析结果不是列表，但是是单个值，则包装成列表
                if not isinstance(parsed_ids, list):
                    return [parsed_ids]
                    
                return parsed_ids
            except (json.JSONDecodeError, ValueError, SyntaxError):
                # 如果所有解析方法都失败，将字符串作为单个ID处理
                return [ids_param]
        
        # 如果不是字符串也不是列表，但有值，则作为单个ID处理
        if ids_param is not None:
            return [ids_param]
            
        return []

    def _handle_error(self, error: Exception) -> Generator[ToolInvokeMessage, None, None]:
        """统一的错误处理"""
        error_msg = str(error)
        yield self.create_json_message({
            "success": False,
            "error": error_msg,
            "error_type": type(error).__name__
        })
    
    def _create_success_message(self, data: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """创建成功响应消息"""
        response = {
            "success": True,
            **data
        }
        yield self.create_json_message(response) 