import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from utils.rabbit_utils import get_rabbit_client
import pika

class RabbitSendPluginTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        queue = tool_parameters.get('Queue')
        message_count = tool_parameters.get('Count')
        messages = []
        if not message_count:
            message_count = 1
        if queue:
            rabbit_client = get_rabbit_client(self.runtime.credentials)
            conn = pika.BlockingConnection(rabbit_client)
            channel = conn.channel()
            # channel.queue_declare(queue=queue)
            # 消费指定条数的消息
            count = 0
            while count < message_count:
                method_frame, header_frame, body = channel.basic_get(queue=queue, auto_ack=True)
                if method_frame:
                    # 如果有消息
                    print(f"Received message: {body.decode()}")
                    messages.append(body.decode())
                    count += 1
                else:
                    print("No more messages.")
                    break
            conn.close()
        yield self.create_text_message(json.dumps(messages))
