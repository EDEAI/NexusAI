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
        question = (tool_parameters.get("question", ''))
        datasets_id = (tool_parameters.get("datasets_ids", ''))
        document_id = (tool_parameters.get("document_ids", ''))
        if datasets_id == None:
            yield self.create_text_message('Dataset id is required')
            return
        datasets_ids = datasets_id.split(",")
        if len(datasets_ids) == 0 and datasets_id != None:
            datasets_ids = [datasets_id]
        document_ids = []    
        if document_id != None and document_id.strip() != '':
            document_ids = document_id.split(",")
            if len(document_ids) == 0:
                document_ids = [document_id]

        parsed_data = {
            "question": question,
            "dataset_ids": datasets_ids,
            "document_ids": document_ids
            }
        print(parsed_data)
        res = client.post(route_method='/api/v1/retrieval', data_obj = parsed_data)
        print(res.json())
        try:
            data = res.json().get("data", res.json().get("message", {}))
            yield self.create_json_message({
                "result": data
            })
        except:
            yield self.create_text_message("Retrieval error")
            return
        
