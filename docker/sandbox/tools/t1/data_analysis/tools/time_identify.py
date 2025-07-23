from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.digitforce_api import DigitForceApi

class TimeIdentifyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            api_key = self.runtime.credentials["digitforce_api_key"]
            query = tool_parameters['query']
            if len(query) > 10000:
                yield self.create_json_message({"message":"The query is too long. Please check if you have entered any incorrect variables"})
            result = DigitForceApi(api_key).dify_api_post({"query":query},"TimeIdentify")
            if result:
                yield self.create_json_message(result)
            else:
                yield self.create_json_message({"message":"response is empty"})
        except Exception as e:
            yield self.create_text_message(str(e))