from typing import Any, List, Dict
from collections.abc import Generator
import json
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .milvus_base import MilvusBaseTool

logger = logging.getLogger(__name__)

class MilvusSearchTool(MilvusBaseTool, Tool):
    """Milvus 向量搜索工具"""

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """执行搜索工具"""
        try:
            # 解析和验证参数
            collection_name = tool_parameters.get("collection_name")
            vector_str = tool_parameters.get("query_vector")

            if not collection_name or not self._validate_collection_name(collection_name):
                raise ValueError("Invalid or missing collection name.")

            if not vector_str:
                raise ValueError("Vector data is required.")

            try:
                vector_data = self._parse_vector_data(vector_str)
            except ValueError as e:
                raise ValueError(str(e))

            # 获取其他参数
            limit = int(tool_parameters.get("limit", 10))
            output_fields_str = tool_parameters.get("output_fields")
            filter_expr = tool_parameters.get("filter")
            search_params_str = tool_parameters.get("search_params")
            anns_field = tool_parameters.get("anns_field", "vector")

            # 准备参数
            search_params = self._parse_search_params(search_params_str)
            output_fields = [f.strip() for f in output_fields_str.split(',')] if output_fields_str else None

            # 执行搜索
            with self._get_milvus_client(self.runtime.credentials) as client:
                if not client.has_collection(collection_name):
                    raise ValueError(f"Collection '{collection_name}' does not exist.")

                logger.info(f"🔍 [DEBUG] Searching in collection '{collection_name}' with limit={limit}, anns_field='{anns_field}'")

                results = client.search(
                    collection_name=collection_name,
                    data=[vector_data],
                    anns_field=anns_field,
                    limit=limit,
                    output_fields=output_fields,
                    filter=filter_expr,
                    search_params=search_params,
                    partition_names=None # partition_names not supported in this tool
                )

                logger.info(f"✅ [DEBUG] Search completed. Found {len(results)} results.")
                
                response_data = {
                    "operation": "search",
                    "collection_name": collection_name,
                    "results": results,
                    "result_count": len(results)
                }
                yield from self._create_success_message(response_data)

        except Exception as e:
            yield from self._handle_error(e)

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