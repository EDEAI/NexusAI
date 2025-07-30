import json
import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.mcp_client import McpClientsUtil


class McpListToolsTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        server_url = tool_parameters.get("server_url", "")
        if not server_url:
            raise ValueError("Please fill in the server_url")
        
        headers = None
        headers_json = tool_parameters.get("headers", "")
        if headers_json:
            try:
                headers = json.loads(headers_json)
            except json.JSONDecodeError as e:
                raise ValueError(f"Headers must be a valid JSON string: {e}")
        
        timeout = tool_parameters.get("timeout", 60)
        sse_read_timeout = tool_parameters.get("sse_read_timeout", 300)

        try:
            tools = McpClientsUtil.fetch_tools(
                server_url=server_url,
                headers=headers,
                timeout=timeout,
                sse_read_timeout=sse_read_timeout
            )
            if not tools:
                yield self.create_text_message("[]")
                return
            yield self.create_text_message(f"{tools}")
        except Exception as e:
            error_msg = f"Error listing MCP Server tools: {str(e)}"
            logging.error(error_msg)
            yield self.create_text_message(error_msg) 