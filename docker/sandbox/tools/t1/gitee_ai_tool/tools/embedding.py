from typing import Any, Generator
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class GiteeAIToolEmbedding(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        headers = {"content-type": "application/json", "authorization": f"Bearer {self.runtime.credentials['api_key']}"}
        payload = {"inputs": tool_parameters.get("inputs")}
        model = tool_parameters.get("model", "bge-m3")
        url = f"https://ai.gitee.com/api/serverless/{model}/embeddings"
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            yield self.create_text_message(f"Got Error Response:{response.text}")
        yield self.create_text_message(response.content.decode("utf-8"))
