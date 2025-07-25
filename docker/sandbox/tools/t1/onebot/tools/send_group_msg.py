from typing import Any, Union, Generator
import requests
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class SendGroupMsg(Tool):
    """OneBot v11 Tool: Send Group Message"""

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        send_group_id = tool_parameters.get("group_id", "")
        if type(send_group_id) is str:
            send_group_id = int(send_group_id)
        message = tool_parameters.get("message", "")
        if not message:
            yield self.create_json_message({"error": "Message is empty."})
        auto_escape = tool_parameters.get("auto_escape", False)
        try:
            url = URL(self.runtime.credentials["ob11_http_url"]) / "send_group_msg"
            resp = requests.post(
                url,
                json={"group_id": send_group_id, "message": message, "auto_escape": auto_escape},
                headers={"Authorization": "Bearer " + self.runtime.credentials["access_token"]},
            )
            if resp.status_code != 200:
                yield self.create_json_message({"error": f"Failed to send group message: {resp.text}"})
            yield self.create_json_message({"response": resp.json()})
        except Exception as e:
            yield self.create_json_message({"error": f"Failed to send group message: {e}"})
