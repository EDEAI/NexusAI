from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from nacos import NacosClient


class NacosTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Extract parameters
        nacos_addr = self.runtime.credentials["nacos_addr"]
        username = self.runtime.credentials["nacos_username"]
        password = self.runtime.credentials["nacos_password"]
        access_key = self.runtime.credentials["nacos_accessKey"]
        secret_key = self.runtime.credentials["nacos_secretKey"]
        namespace_id = str(tool_parameters['namespace_id'])
        data_id = str(tool_parameters['data_id'])
        group_name = str(tool_parameters['group_name'])
        client = NacosClient(nacos_addr, namespace=namespace_id,
                             username=username, password=password,
                             ak=access_key, sk=secret_key)
        content = str(tool_parameters['content'])
        try:
            publish_result = client.publish_config(data_id=data_id, group=group_name, content=content)
            yield self.create_json_message({
                "success": True,
                "result": publish_result
            })

        except Exception as e:
            yield self.create_json_message({
                "success": False,
                "error": str(e)
            })
