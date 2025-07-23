from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.database_utils import DBSchemaExtractor
from tools.dify_knowledge_api_utils import DifyKnowledgeRequest

class DatabaseToKnowledgeTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        extractor = DBSchemaExtractor(
            tool_parameters.get("db_type"),
            tool_parameters.get("host"),
            tool_parameters.get("port"),
            tool_parameters.get("username"),
            tool_parameters.get("password"),
            tool_parameters.get("database"),
            tool_parameters.get("properties")
        )

        dify_knowledge_api_url = self.runtime.credentials.get("dify_knowledge_api_url")
        dify_knowledge_api_key = self.runtime.credentials.get("dify_knowledge_api_key")

        embedding_model = tool_parameters.get("embedding_model")
        rerank_model = tool_parameters.get("rerank_model")

        api = DifyKnowledgeRequest(dify_knowledge_api_url, dify_knowledge_api_key, embedding_model, rerank_model)
        dataset_id = api.write_database_schema(extractor.get_all_tables_schema(tool_parameters.get("table_names")), tool_parameters.get("database"))

        yield self.create_text_message(dataset_id)
