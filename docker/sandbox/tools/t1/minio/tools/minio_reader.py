from collections.abc import Generator
from typing import Any

import io
from werkzeug import Request, Response
from minio import Minio
from minio.error import S3Error
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class MinioWriterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        # 从参数中获取内容和对象名称
        object_name = tool_parameters.get("object_name")
        # 从运行时凭据中获取MinIO配置
        access_key = tool_parameters.get("access_key")

        secret_key = tool_parameters.get("secret_key")

        endpoint = tool_parameters.get("endpoint")

        bucket_name = tool_parameters.get("bucket_name")

        # 初始化 MinIO 客户端
        client = Minio(
            endpoint.replace("http://", "").replace("https://", ""),  # MinIO 客户端不需要协议头
            access_key=access_key,
            secret_key=secret_key,
            secure=endpoint.startswith("https://")  # 根据协议判断是否启用 HTTPS
        )
        try:
            # 获取对象内容
            response = client.get_object(bucket_name, object_name)
        
            content = response.read().decode("utf-8")  # 假设是文本文件，按 UTF-8 解码
            response.close()
            response.release_conn()

            # 返回结果
            
            yield self.create_text_message(content)
        except S3Error as e:
            raise Exception(f"Failed to read from MinIO: {str(e)}")
        except Exception as e:
            raise Exception(f"An error occurred: {str(e)}")