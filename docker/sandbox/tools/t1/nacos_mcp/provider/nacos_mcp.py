import asyncio
from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService
from maintainer.common.ai_maintainer_client_config_builder import \
    AIMaintainerClientConfigBuilder

import logging
from dify_plugin.config.logger_format import plugin_logger_handler

# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)


class NacosMcpProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:

        async def validate_credentials() -> None:
            try:
                nacos_addr = credentials.get("nacos_addr")
                if not nacos_addr:
                    raise ToolProviderCredentialValidationError(
                        "nacos_addr is required")
                nacos_username = credentials.get("nacos_username")
                nacos_password = credentials.get("nacos_password")
                nacos_access_key = credentials.get("nacos_accessKey")
                nacos_secret_key = credentials.get("nacos_secretKey")

                ai_client_config = AIMaintainerClientConfigBuilder().server_address(
                        nacos_addr).username(
                        nacos_username).password(
                        nacos_password).access_key(
                        nacos_access_key).secret_key(
                        nacos_secret_key).build()
                mcp_service = await NacosAIMaintainerService.create_mcp_service(ai_client_config)
                await mcp_service.list_mcp_servers("public","",1,10)
            except Exception as e:
                raise ToolProviderCredentialValidationError(str(e))

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(validate_credentials())
        except Exception as e:
            logger.error(f"Error calling tool: {e}")
            raise

