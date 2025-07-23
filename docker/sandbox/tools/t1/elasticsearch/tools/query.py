import json
from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from tools.base import ElasticsearchBaseTool
from dify_plugin.entities.tool import ToolInvokeMessage


class ElasticsearchQueryTool(Tool, ElasticsearchBaseTool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        client = self.from_credential(credentials=self.runtime.credentials)
        index = tool_parameters.get("index")
        query = tool_parameters.get("query")
        from_ = tool_parameters.get("from", 0)
        size = tool_parameters.get("size", 10)
        source_includes = tool_parameters.get("source_includes", "*")
        sort = tool_parameters.get("sort", None)
        resp = client.search(
            index=index,
            query=json.loads(query),
            from_=from_,
            size=size,
            source_includes=source_includes,
            sort=sort if sort else None,
        )
        result = []
        for hit in resp["hits"]["hits"]:
            result.append(hit["_source"])
        yield self.create_text_message(json.dumps(result))
        yield self.create_json_message({"result": result})
