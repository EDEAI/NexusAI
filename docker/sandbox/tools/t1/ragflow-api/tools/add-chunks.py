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
        content = (tool_parameters.get("content", ''))
        datasets_id = (tool_parameters.get("datasets_id", ''))
        document_id = (tool_parameters.get("document_id", ''))
        if datasets_id == None or document_id == None:
            yield self.create_text_message('Please enter the dataset id and document id')
            return
        
        parsed_data = {"content": content}
        res = client.post(route_method='/api/v1/datasets/' + datasets_id + '/documents/' + document_id + '/chunks', data_obj = parsed_data)
        try:
            chunk = res.json().get("data", {}).get("chunk", {})
            yield self.create_json_message({
                "result": chunk
            })
        except:
            yield self.create_text_message("insert failed")
            return
        
