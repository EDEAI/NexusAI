from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from zep_cloud.client import Zep
from zep_cloud.errors import BadRequestError


class InitSessionTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["zep_api_key"]
            client = Zep(api_key=api_key)

            try:
                client.memory.add_session(
                    user_id=tool_parameters["user_id"],
                    session_id=tool_parameters["session_id"],
                )
            except BadRequestError as e:
                # bad request error could only happen if the session already exists, which is fine
                pass

            yield self.create_json_message({"status": "success"})
        except Exception as e:
            err = str(e)
            yield self.create_json_message({"status": "error", "error": err})
