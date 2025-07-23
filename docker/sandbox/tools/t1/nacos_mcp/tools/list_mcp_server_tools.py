import asyncio
import random
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from maintainer.ai.model.nacos_mcp_info import McpServerDetailInfo, McpToolMeta
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService
from maintainer.common.ai_maintainer_client_config_builder import \
    AIMaintainerClientConfigBuilder

import logging
from dify_plugin.config.logger_format import plugin_logger_handler
from mcp import ClientSession, types
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client

from utils.nacos_utils import update_tools_according_to_nacos


# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class ListTools(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        def get_clients(_protocol:str, _url:str):
            if _protocol == "mcp-sse":
                return sse_client(url=_url)
            elif _protocol == "mcp-streamable":
                return streamablehttp_client(url=_url)

        async def get_tools(_protocol:str, _url:str):
            async with get_clients(_protocol, _url) as (_read, _write):
                async with ClientSession(_read, _write) as _session:
                    await _session.initialize()
                    _tools = await _session.list_tools()
                    return _tools

        async def list_mcp_servers_tools():
            nacos_addr = self.runtime.credentials["nacos_addr"]
            username = self.runtime.credentials["nacos_username"]
            password = self.runtime.credentials["nacos_password"]
            access_key = self.runtime.credentials["nacos_accessKey"]
            secret_key = self.runtime.credentials["nacos_secretKey"]
            namespace_id = tool_parameters["namespace_id"]
            if namespace_id is None or len(namespace_id) == 0:
                namespace_id = "public"
            mcp_server_names = tool_parameters["mcp_server_name"]

            ai_client_config = AIMaintainerClientConfigBuilder().server_address(
                    nacos_addr).username(
                    username).password(
                    password).access_key(
                    access_key).secret_key(
                    secret_key).build()
            mcp_service = await NacosAIMaintainerService.create_mcp_service(
                    ai_client_config)

            server_names_list = mcp_server_names.split(";")
            result = []
            for server_name in server_names_list:
                original_name = server_name
                name_and_version = server_name.split("::")
                version = ""
                if len(name_and_version) == 2:
                    version = name_and_version[1]
                    server_name = name_and_version[0]
                elif len(name_and_version)>2:
                    raise Exception("mcp_server_name format error")

                try:
                    mcp_server_detail_info = await mcp_service.get_mcp_server_detail(namespace_id, server_name, version)
                except Exception as e:
                    logger.info(f"get mcp server detail error: {e}")
                    continue

                if mcp_server_detail_info.protocol != "mcp-sse" and mcp_server_detail_info.protocol != "mcp-streamable":
                    continue
                endpoint_list = mcp_server_detail_info.backendEndpoints
                export_path = mcp_server_detail_info.remoteServerConfig.exportPath
                if endpoint_list and len(endpoint_list) >0:
                    random_index = random.randint(0, len(endpoint_list)-1)
                    address = endpoint_list[random_index].address
                    port = endpoint_list[random_index].port
                    if port == 443:
                        http_schema = "https"
                    else:
                        http_schema = "http"
                    url = "{0}://{1}:{2}{3}".format(http_schema, address, str(port),export_path)
                    if not export_path.startswith("/"):
                        url = "{0}://{1}:{2}/{3}".format(http_schema,address,str(port),export_path)
                    tools = await get_tools(mcp_server_detail_info.protocol, url)

                    tools = update_tools_according_to_nacos(tools, mcp_server_detail_info)

                    mcp_name_tools_list = {
                        "name": original_name,
                        "tools": tools
                    }

                    result.append(mcp_name_tools_list)

            return result


        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(list_mcp_servers_tools())
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            raise

        yield self.create_json_message({
            "result":result
        })
