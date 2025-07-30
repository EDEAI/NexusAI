from collections.abc import Generator
import os
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from qiniu import Auth, put_file, etag
import qiniu.config
import requests
import uuid
import time


class QiniuTool(Tool):
    def _parse_response(self, response: dict, base_url: str) -> dict:
        result = {}
        if response.get("hash"):
            result["hash"] = response.get("hash", "")
            result["key"] = response.get("key", "")
            result["url"] = f"{base_url}{result['key']}" if base_url != "" else ""
        return result

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        dify_url = os.getenv("DIFY_INNER_API_URL")
        access_key = self.runtime.credentials["access_key"]
        secret_key = self.runtime.credentials["secret_key"]
        if not access_key or not secret_key:
            raise ValueError("access_key and secret_key are required")
        # 要上传的空间
        bucket_name = tool_parameters.get("bucket_name")
        if not bucket_name:
            raise ValueError("bucket_name is required")
        # 上传后保存的文件名
        key = tool_parameters.get("key")
        if not key:
            key = time.strftime("%Y%m%d%H%M%S") + "-" + str(uuid.uuid4())
        # 要上传文件的本地路径
        filePath = tool_parameters.get("filePath")
        upload_files = tool_parameters.get("upload_files")
        if not filePath and not upload_files:
            raise ValueError("filePath or upload_files is required")
        base_url = tool_parameters.get("base_url")
        if filePath:
            key = key + "." + filePath.split(".")[-1]
            if filePath.startswith("http"):
                file_url = filePath
                filePath = f"/tmp/{str(uuid.uuid4())}"
                with open(filePath, "wb") as f:
                    f.write(requests.get(file_url).content)

        if not base_url:
            base_url = ""
        if base_url != "":
            if not base_url.startswith("http") and not base_url.startswith("https"):
                raise ValueError("base_url must start with http or https")
            if not base_url.endswith("/"):
                base_url += "/"

        # 如果filePath为空，则从upload_files中获取文件
        if not filePath:
            # print(upload_files)
            file_url = upload_files[0].url
            key = key + "-" + upload_files[0].extension
            # 随机生成文件名
            file_name = str(uuid.uuid4())
            # save file to local
            filePath = f"/tmp/{file_name}"
            with open(filePath, "wb") as f:
                file_url = dify_url+file_url if dify_url is not None else file_url
                f.write(requests.get(
                    file_url).content)
        # 构建鉴权对象
        q = Auth(access_key, secret_key)
        # 生成上传 Token，可以指定过期时间等
        token = q.upload_token(bucket_name, key, 3600)
        # 要上传文件的本地路径
        ret, info = put_file(token, key, filePath, version='v2')
        # 解析响应
        result = self._parse_response(ret, base_url)
        yield self.create_json_message({
            "result": result
        })
