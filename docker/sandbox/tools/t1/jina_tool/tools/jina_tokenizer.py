import requests
from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class JinaTokenizerTool(Tool):
    _jina_tokenizer_endpoint = "https://tokenize.jina.ai/"

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        content = tool_parameters["content"]
        body = {"content": content}
        headers = {"Content-Type": "application/json"}
        if "api_key" in self.runtime.credentials and self.runtime.credentials.get("api_key"):
            headers["Authorization"] = "Bearer " + self.runtime.credentials.get("api_key")
        if tool_parameters.get("return_chunks", False):
            body["return_chunks"] = True
        if tool_parameters.get("return_tokens", False):
            body["return_tokens"] = True
        if tokenizer := tool_parameters.get("tokenizer"):
            body["tokenizer"] = tokenizer
        response = requests.post(self._jina_tokenizer_endpoint, headers=headers, json=body)
        yield self.create_json_message(response.json())
