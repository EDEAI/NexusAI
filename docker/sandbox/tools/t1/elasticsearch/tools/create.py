import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from tools.base import ElasticsearchBaseTool
from dify_plugin.entities.tool import ToolInvokeMessage


class ElasticsearchAddDocumentTool(Tool, ElasticsearchBaseTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = self.from_credential(credentials=self.runtime.credentials)
        index = tool_parameters.get("index")
        document_id = tool_parameters.get("document_id")
        document = tool_parameters.get("document")
        resp = client.create(index=index, id=document_id, document=json.loads(document))
        yield self.create_text_message(json.dumps(resp.raw))
