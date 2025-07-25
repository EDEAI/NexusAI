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
        keywords = (tool_parameters.get("keywords", ''))
        datasets_id = (tool_parameters.get("datasets_id", ''))
        document_id = (tool_parameters.get("document_id", ''))
        page = tool_parameters.get("page")
        page_size = tool_parameters.get("page_size")
        if datasets_id == None or document_id == None:
            yield self.create_text_message('Please enter the dataset id and document id')
            return
        
        parsed_data = {"name": keywords, "page": page, "page_size": page_size}
        res = client.get(route_method='/api/v1/datasets/' + datasets_id + '/documents/' + document_id + '/chunks', params = parsed_data)
        try:
            chunks = res.json().get("data", {}).get("chunks", [])
            if len(chunks) == 0:
                yield self.create_text_message("No chunks found")
            else:
                yield self.create_json_message({
                    "result": chunks
                })
        except:
            yield self.create_text_message("Error occurred while processing the response")
            return
        
