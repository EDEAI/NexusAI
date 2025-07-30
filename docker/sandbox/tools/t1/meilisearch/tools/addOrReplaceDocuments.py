from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
import ast, requests

class addOrReplaceDocuments(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        documents = ast.literal_eval(tool_parameters["documents"])
        response = requests.post(
            f"{self.runtime.credentials['base_url']}/indexes/{tool_parameters['indexUid']}/documents",
            headers={"Authorization": f"Bearer {self.runtime.credentials['meilisearch_api_key']}",
                     "Content-Type": "application/json"},
            json=documents
        )
        yield self.create_json_message(response.json())

