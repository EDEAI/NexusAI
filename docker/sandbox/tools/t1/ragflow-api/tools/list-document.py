from collections.abc import Generator
from typing import Any
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ragflow_api import RagflowClient
import re

class RagflowApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        app_id = str(self.runtime.credentials.get("app_key"))
        app_url = str(self.runtime.credentials.get("app_url"))

        client = RagflowClient(app_id, app_url)
        name = (tool_parameters.get("name", ''))
        datasets_id = (tool_parameters.get("datasets_id", ''))
        
        parsed_data = {"name": name}
        res = client.get(route_method='/api/v1/datasets/' + datasets_id + '/documents', params = parsed_data)
        try:
            docs = res.json().get("data", {}).get("docs", [])
            if len(docs) == 0:
                yield self.create_text_message("No documents found")
            elif docs[0].get("run", '') == "FAIL":
                yield self.create_text_message("Document parsing status failed")
            elif docs[0].get("run", '') == "DONE" or docs[0].get("run", '') == "0":
                yield self.create_text_message(docs[0].get("id", ''))
            else:
                yield self.create_text_message("Document parsing status is in progress")
        except:
            yield self.create_text_message("Error occurred while processing the response")
            return
        
