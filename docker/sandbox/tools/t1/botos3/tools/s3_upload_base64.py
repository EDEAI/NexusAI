from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import boto3
from botocore.config import Config
import base64
import io

class S3UploadBase64(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.runtime.credentials["S3_ENDPOINT"],
            aws_access_key_id=self.runtime.credentials["S3_ACCESS_KEY"],
            aws_secret_access_key=self.runtime.credentials["S3_SECRET_KEY"],
            config=Config(signature_version='s3v4'),
            verify=False
        )
        bucket_name = self.runtime.credentials["BUCKET_NAME"]
        s3_key = tool_parameters.get("s3_key")
        file_base64 = tool_parameters.get("file_base64")
        # 解码base64字符串
        binary_data = base64.b64decode(file_base64)
    
        # 创建文件对象
        file_obj = io.BytesIO(binary_data)
        self.s3_client.upload_fileobj(
            file_obj,
            bucket_name,
            s3_key
        )
        url = f"{self.runtime.credentials["S3_PUBLIC_URL"]}/{s3_key}"
        yield self.create_text_message(url)

    
