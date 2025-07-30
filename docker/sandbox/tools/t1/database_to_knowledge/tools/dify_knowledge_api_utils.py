from typing import Optional, Any

import time
import httpx
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


def auth(credentials):
    dify_knowledge_api_url = credentials.get("dify_knowledge_api_url")
    dify_knowledge_api_key = credentials.get("dify_knowledge_api_key")
    if not dify_knowledge_api_url or not dify_knowledge_api_key:
        raise ToolProviderCredentialValidationError("dify_knowledge_api_url and dify_knowledge_api_key is required")
    try:
        assert DifyKnowledgeRequest(dify_knowledge_api_url, dify_knowledge_api_key).validate_api_key is True
    except Exception as e:
        raise ToolProviderCredentialValidationError(str(e))


class DifyKnowledgeRequest:
    def __init__(self, dify_knowledge_api_url: str, dify_knowledge_api_key: str, embedding_model: Optional[dict] = None, rerank_model: Optional[dict] = None):
        self.dify_knowledge_api_url = dify_knowledge_api_url
        self.dify_knowledge_api_key = dify_knowledge_api_key
        self.embedding_model = embedding_model
        self.rerank_model = rerank_model

    # 用来当做鉴权
    @property
    def validate_api_key(self) -> bool:
        url = f"{self.dify_knowledge_api_url}/datasets"
        params = {
            "page": 1,
            "limit": 1
        }
        res = self._send_request(url, method="get", params=params)
        return res.get("data") is not None

    def _send_request(self, url: str, method: str = "post", json: Optional[dict] = None, params: Optional[dict] = None, ) -> dict:
        headers = {
            "Authorization": f"Bearer {self.dify_knowledge_api_key}",
            "Content-Type": "application/json",
        }
        response = httpx.request(method=method, url=url, headers=headers, json=json, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def _create_dataset(self, dataset_name: str) -> str:
        """
        创建知识库
        :param dataset_name: 知识库名称
        :return: 知识库ID
        """
        url = f"{self.dify_knowledge_api_url}/datasets"
        json = {
            "name": f'{dataset_name}-{int(time.time())}',
            "description": f"Metadata of {dataset_name}",
            "indexing_technique": "high_quality",
            "permission": "all_team_members",
            "provider": "vendor"
        }
        res = self._send_request(url, json=json)
        return res.get("id")

    def _create_document_by_text(self, dataset_id: str, document_name: str, document_text: str) -> dict[str, Any]:
        """
        创建文档
        :param dataset_id: 知识库ID
        :param document_name: 文档名称
        :param document_text: 文档内容
        :return: 知识库ID
        """
        url = f"{self.dify_knowledge_api_url}/datasets/{dataset_id}/document/create-by-text"
        json: dict = {
            "name": document_name,
            "text": document_text,
            "doc_metadata": [],
            "indexing_technique": "high_quality",
            "doc_form": "hierarchical_model",
            "doc_language": "Chinese",
            "process_rule": {
                "mode": "hierarchical",
                "rules": {
                    "pre_processing_rules": [
                        {"id": "remove_extra_spaces", "enabled": True},
                        {"id": "remove_urls_emails", "enabled": False}
                    ],
                    "segmentation": {"separator": "\n\n", "max_tokens": 4000},
                    "parent_mode": "paragraph",
                    "subchunk_segmentation": {"separator": "\n", "max_tokens": 4000}
                }
            },
            "retrieval_model": {
                "search_method": "semantic_search",
                "reranking_enable": True,
                "reranking_model": {
                    "reranking_model_name": self.rerank_model.get("model"),
                    "reranking_provider_name": self.rerank_model.get("provider"),
                },
                "top_k": 10,
                "score_threshold_enabled": False
            },
            "embedding_model": self.embedding_model.get("model"),
            "embedding_model_provider": self.embedding_model.get("provider"),
        }

        res = self._send_request(url, json=json)
        return res.get("document")

    def write_database_schema(self, schema: dict[str, Any], database: str) -> str:
        """
        将数据库schema写入知识库
        :param schema: 数据库schema信息
        :param database: 数据库名
        """
        try:
            # 创建知识库
            dataset_id = self._create_dataset(dataset_name=database)

            # 为每个表创建文档
            for table_name, table_info in schema.items():
                # 构建文档内容
                document_name = f"{table_info["comment"]}({table_name})"
                document_text = f"{table_name}:{table_info["comment"]}\n字段列表:\n"

                # 添加字段信息
                for column in table_info["columns"]:
                    document_text += f"{column["name"]}|{column["type"]}|{column["comment"]}\n"

                # 创建文档
                document_dict = self._create_document_by_text(dataset_id=dataset_id, document_name=document_name, document_text=f'{document_text}\n')
                if document_dict is None:
                    raise ValueError("Failed to create document")

            return dataset_id
        except Exception as e:
            print(f"Metadata writing to knowledge failed: {str(e)}")
            raise
