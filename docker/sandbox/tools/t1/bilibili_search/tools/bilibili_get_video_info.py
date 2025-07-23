from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.util import parse_cookies, get_video_info


class BilibiliGetVideoInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        bvid = tool_parameters.get("bvid", None)
        if not bvid:
            raise ValueError("BVID is required")

        cookies = self.runtime.credentials.get("cookies", None)
        res = get_video_info(
            bvid=bvid,
            cookies=parse_cookies(cookies),
        )

        yield self.create_json_message(res.data.model_dump())
