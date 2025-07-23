from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.rabbit_utils import get_rabbit_client
import pika
import json

class RabbitSendPluginTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        exchange = tool_parameters.get('Exchange')
        routing_key = tool_parameters.get('RoutingKey')
        message = tool_parameters.get('Message')
        if exchange and routing_key and message:
            rabbit_client = get_rabbit_client(self.runtime.credentials)
            conn = pika.BlockingConnection(rabbit_client)
            conn.channel().basic_publish(exchange=exchange, routing_key=routing_key, body=message)
            conn.close()
        yield self.create_json_message({
            "result": f"Sent: {message} to exchange {exchange} with routing key {routing_key}"
        })
