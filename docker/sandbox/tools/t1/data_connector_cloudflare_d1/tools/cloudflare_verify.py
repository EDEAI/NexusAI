from collections.abc import Generator
from typing import Any

from utils.cloudflare_d1 import cloudflare_token_verify

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class CloudflareVerify(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            if tool_parameters["a_cloudflare_api_token"]:
                api_token = tool_parameters["a_cloudflare_api_token"]
            else:
                api_token = self.runtime.credentials["cloudflare_api_token"]
        except KeyError:
            api_token = self.runtime.credentials["cloudflare_api_token"]
        result = cloudflare_token_verify(api_token)
        yield self.create_json_message(result)
