import json
import logging
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.mcp_client import McpClients


class McpTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        servers_config_json = tool_parameters.get("servers_config") or self.runtime.credentials.get("servers_config")
        if not servers_config_json:
            raise ValueError("Please fill in the servers_config")
        try:
            servers_config = json.loads(servers_config_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"servers_config must be a valid JSON string: {e}")

        resources_as_tools = tool_parameters.get("resources_as_tools", False)
        prompts_as_tools = tool_parameters.get("prompts_as_tools", False)

        mcp_clients = None
        try:
            mcp_clients = McpClients(servers_config, resources_as_tools, prompts_as_tools)
            tools = mcp_clients.fetch_tools()
            prompt_tools = [to_prompt_tool(tool) for tool in tools]
            yield self.create_text_message(f"MCP Server tools list: \n{prompt_tools}")
        except Exception as e:
            error_msg = f"Error listing MCP Server tools: {e}"
            logging.error(error_msg)
            yield self.create_text_message(error_msg)
        finally:
            if mcp_clients:
                mcp_clients.close()


def to_prompt_tool(tool: dict) -> dict[str, Any]:
    """
    Tool to prompt message tool
    """
    return {
        "name": tool.get("name"),
        "description": tool.get("description", ""),
        "parameters": tool.get("inputSchema"),
    }
