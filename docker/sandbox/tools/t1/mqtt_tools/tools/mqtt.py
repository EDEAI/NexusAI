from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import threading
import queue
from enum import Enum

import paho.mqtt.subscribe as subscribe
import paho.mqtt.publish as publish

class MqttTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        ctype = tool_parameters["type"]
        broker = tool_parameters["broker"]
        port = tool_parameters["port"]
        topic = tool_parameters["topic"]
        pld = tool_parameters["payload"]
        #print(f"cmd{ctype} b{broker} p{port} t{topic} p{pld}")

        res = ""

        if ctype == "pub":
            publish.single(topic, pld, hostname=broker, port=port, qos=1)
            res = "0"
        elif ctype == "sub":
            msg = subscribe.simple(topic, hostname=broker, port=port)
            res = str(msg.payload, 'utf-8')
        else:
            res = "-1" # TODO More errnos

        yield self.create_text_message(res)
