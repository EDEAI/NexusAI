from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import boto3
from botocore.config import Config
import base64
import io
import requests

class S3UploadFile(Tool):
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
        file = tool_parameters.get("file")
        s3_key = tool_parameters.get("s3_key")
        file_url = tool_parameters.get("file_url")
        if not file_url:
            file_url = file.url
            if not file_url.startswith("http"):
                file_url = self.runtime.credentials["DIFY_ENDPOINT"] + file.url
        response = requests.get(file_url, stream=True, verify=False)
        response.raw.decode_content = True
        response.raise_for_status()

        # 上传到 S3
        self.s3_client.upload_fileobj(
            response.raw,
            bucket_name,
            s3_key
        )
        url = f"{self.runtime.credentials["S3_PUBLIC_URL"]}/{s3_key}"
        yield self.create_text_message(url)

    
