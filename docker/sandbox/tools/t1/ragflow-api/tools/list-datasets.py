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
        page_param = tool_parameters.get("page")
        page = int(page_param) if page_param is not None else 1
        
        page_size_param = tool_parameters.get("page_size")
        page_size = int(page_size_param) if page_size_param is not None else 30

        parsed_data = {"page": page, "page_size": page_size}

        res = client.get(route_method='/api/v1/datasets', params = parsed_data)
        # print(res.json())
        try:
            data = res.json().get("data", {})
            if len(data) == 0:
                yield self.create_text_message("No datasets found")
                return
            yield self.create_json_message({
                "result": data
            })
        except:
            yield self.create_text_message("Error occurred while processing the response")
            return
        
