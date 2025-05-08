import asyncio

from contextlib import AsyncExitStack
from datetime import datetime
from log import Logger
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.sse import sse_client

from config import settings


project_root = Path(__file__).parent.parent.parent
logger = Logger.get_logger('chatroom')


class MCPClient:
    def __init__(self):
        self._session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    async def connect_to_server(self):
        client = sse_client(f'http://localhost:{settings.MCP_SERVER_PORT}/sse', timeout=10)
        sse_transport = await self._exit_stack.enter_async_context(client)
        self._session = await self._exit_stack.enter_async_context(ClientSession(*sse_transport))

        await self._session.initialize()

        # List available tools
        response = await self._session.list_tools()
        tools = response.tools
        logger.info(f'Successfully connected to server with tools: {[tool.name for tool in tools]}')

    async def get_tool_list(self) -> List[Dict[str, Any]]:
        response = await self._session.list_tools()
        return [tool.model_dump() for tool in response.tools]

    async def call_tool(self, tool_name: str, tool_input: Optional[Dict[str, Any]] = None) -> str:
        response = await self._session.call_tool(tool_name, tool_input)
        return response.content[0].text

    async def cleanup(self):
        '''Clean up resources'''
        await self._exit_stack.aclose()
    