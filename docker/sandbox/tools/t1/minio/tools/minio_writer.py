from collections.abc import Generator
from typing import Any

import io
from minio import Minio
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class MinioWriterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        # 从参数中获取内容和对象名称
        content = tool_parameters.get("content")
        object_name = tool_parameters.get("object_name")
        print(content)
        print(object_name)
        if not content or not object_name:
            yield self.create_json_message({"message": "Content and object_name are required"})
            return
        
        # 从运行时凭据中获取MinIO配置
        access_key = tool_parameters.get("access_key")
        print(access_key)

        secret_key = tool_parameters.get("secret_key")
        print(secret_key)

        endpoint = tool_parameters.get("endpoint")
        print(endpoint)
        bucket_name = tool_parameters.get("bucket_name")
        print(bucket_name)

        try:
            # 初始化MinIO客户端
            minio_client = Minio(
                endpoint.replace("http://", "").replace("https://", ""),
                access_key=access_key,
                secret_key=secret_key,
                secure=endpoint.startswith("https://")
            )

            # 确保存储桶存在
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)

            # 将内容转为字节流并上传
            content_bytes = content.encode("utf-8")
            content_stream = io.BytesIO(content_bytes)
            minio_client.put_object(
                bucket_name,
                object_name,
                content_stream,
                length=len(content_bytes),
                content_type="text/plain"
            )

            # 返回成功消息
            yield self.create_text_message(f"Content successfully written to {bucket_name}/{object_name}")
        except Exception as e:
            yield self.create_json_message({"message": f"Write Failed: {str(e)}"})
            return
        return {
            "status": "success"
        }