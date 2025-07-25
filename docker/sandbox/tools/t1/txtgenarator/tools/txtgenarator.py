from collections.abc import Generator
from typing import Any
import base64

from flask import send_file
from io import BytesIO

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class TxtgenaratorTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        title = tool_parameters.get("title", "")
        content = tool_parameters.get("query", "")
        #
        # # 处理title，避免非法字符
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        filename = f"{safe_title}.txt"
        #
        # # 将内容编码成 base64，不用落盘了
        content_bytes = content.encode('utf-8')
        # content_base64 = base64.b64encode(content_bytes).decode('utf-8')

        # 返回json，带上文件名、内容、MIME类型
        yield self.create_blob_message(content_bytes,meta={"file_name":filename,'mime_type':'text/plain'})
