from collections.abc import Generator
from typing import Any
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils import create_opensearch_client


class OpenSearchTool(Tool):

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = create_opensearch_client(self.runtime.credentials)

        index = tool_parameters.get('index')
        _query = tool_parameters.get('query')
        query = json.loads(_query)
        from_ = tool_parameters.get('from', 0)
        size = tool_parameters.get('size', 10)

        try:
            resp = client.search(
                index=index,
                body=query,
                from_=from_,
                size=size
            )
            hits = resp['hits']
            result = [hit['_source'] for hit in hits['hits']]
            yield self.create_text_message(json.dumps(result, ensure_ascii=False, indent=2))
            yield self.create_variable_message('total', hits['total']['value'])
            yield self.create_variable_message('message', 'ok')
            yield self.create_variable_message('result', result)
        except Exception as e:
            yield self.create_text_message('empty response')
            yield self.create_variable_message('total', 0)
            yield self.create_variable_message('message', repr(e))
            yield self.create_variable_message('result', [])
