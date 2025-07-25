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
        parsed_data = {"name": name}
        res = client.get(route_method='/api/v1/datasets', params = parsed_data)
        # print(res.json())
        try:
            data = res.json().get("data", {})
            if len(data) == 0:
                yield self.create_text_message("0")
            else:
                yield self.create_text_message(data[0].get("id", ''))
            return
        except:
            yield self.create_text_message("0")
            return
        
