from typing import Any, Union, Generator
import requests
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class SendPrivateMsg(Tool):
    """OneBot v11 Tool: Send Private Message"""

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        send_user_id = tool_parameters.get("user_id", "")
        if type(send_user_id) is str:
            send_user_id = int(send_user_id)
        message = tool_parameters.get("message", "")
        if not message:
            yield self.create_json_message({"error": "Message is empty."})
        auto_escape = tool_parameters.get("auto_escape", False)
        try:
            url = URL(self.runtime.credentials["ob11_http_url"]) / "send_private_msg"
            resp = requests.post(
                url,
                json={"user_id": send_user_id, "message": message, "auto_escape": auto_escape},
                headers={"Authorization": "Bearer " + self.runtime.credentials["access_token"]},
            )
            if resp.status_code != 200:
                yield self.create_json_message({"error": f"Failed to send private message: {resp.text}"})
            yield self.create_json_message({"response": resp.json()})
        except Exception as e:
            yield self.create_json_message({"error": f"Failed to send private message: {e}"})
