from contextlib import AsyncExitStack
from log import Logger
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp import ClientSession
from mcp.client.sse import sse_client

from config import settings


project_root = Path(__file__).parent.parent.parent


class MCPClient:
    def __init__(self):
        self._servers: Dict[str, ClientSession] = {}
        self._tool_name_to_server_name: Dict[str, str] = {}
        self._exit_stack = AsyncExitStack()
        
    async def connect_to_builtin_server(self):
        client = sse_client(f'http://localhost:{settings.MCP_SERVER_PORT}/sse')
        sse_transport = await self._exit_stack.enter_async_context(client)
        session = await self._exit_stack.enter_async_context(ClientSession(*sse_transport))
        await session.initialize()
        self._servers['builtin'] = session
        response = await session.list_tools()
        for tool in response.tools:
            self._tool_name_to_server_name[tool.name] = 'builtin'

    async def connect_to_server(self, server_name: str, server_config: Dict[str, Any]):
        raise NotImplementedError('Not implemented')

    async def get_tool_list(self) -> List[Dict[str, Any]]:
        tool_list = []
        for session in self._servers.values():
            response = await session.list_tools()
            for tool in response.tools:
                tool_list.append(tool.model_dump())
        return tool_list

    async def call_tool(self, tool_name: str, tool_input: Optional[Dict[str, Any]] = None) -> str:
        server_name = self._tool_name_to_server_name[tool_name]
        response = await self._servers[server_name].call_tool(tool_name, tool_input)
        return response.content[0].text

    async def cleanup(self):
        '''Clean up resources'''
        await self._exit_stack.aclose()
    