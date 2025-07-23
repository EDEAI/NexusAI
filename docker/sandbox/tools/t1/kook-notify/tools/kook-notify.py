from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from khl.card import Card, Module

from tools.client import send_to_kook
from tools.model import Input


class DifyPluginPdmTemplateTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        input = Input.model_validate(tool_parameters)

        try:
            card = Card(
                Module.Header(input.title),
                Module.Section(input.content),
                Module.Context(f"{input.type.value} message from Dify"),
                color=input.type.color,
            )

            send_to_kook(
                card=card,
                credentials=self.runtime.credentials,
            )

            yield self.create_json_message({"result": "Send Kook message success"})
        except Exception as e:
            yield self.create_text_message(
                f"Error while sending Kook message: {str(e)}"
            )

