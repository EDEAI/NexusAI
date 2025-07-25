import asyncio
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService
from maintainer.common.ai_maintainer_client_config_builder import \
    AIMaintainerClientConfigBuilder


import logging
from dify_plugin.config.logger_format import plugin_logger_handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class ListServers(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        async def list_mcp_servers():
            nacos_addr = self.runtime.credentials["nacos_addr"]
            username = self.runtime.credentials["nacos_username"]
            password = self.runtime.credentials["nacos_password"]
            access_key = self.runtime.credentials["nacos_accessKey"]
            secret_key = self.runtime.credentials["nacos_secretKey"]
            namespace_id = tool_parameters["namespace_id"]
            if namespace_id is None or len(namespace_id) == 0:
                namespace_id = "public"
            page_no = tool_parameters["page_no"]
            page_size = tool_parameters["page_size"]

            ai_client_config = AIMaintainerClientConfigBuilder().server_address(
                    nacos_addr).username(
                    username).password(
                    password).access_key(
                    access_key).secret_key(
                    secret_key).build()
            mcp_service = await NacosAIMaintainerService.create_mcp_service(
                    ai_client_config)

            total_count, page_num, page_available,mcp_servers = await mcp_service.list_mcp_servers(namespace_id,"",page_no,page_size)
            result = {
                "totalCount": total_count,
                "pageNumber": page_num,
                "pagesAvailable": page_available,
            }

            mcp_server_list = []
            for mcp_server in mcp_servers:
                if mcp_server.protocol == "mcp-sse" or mcp_server.protocol == "mcp-streamable":
                    server = {
                        "name": mcp_server.name,
                        "description": mcp_server.description
                    }
                    mcp_server_list.append(server)

            result["mcp_server_list"] = mcp_server_list

            return result

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(list_mcp_servers())
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            raise

        yield self.create_json_message({
            "result":result
        })
