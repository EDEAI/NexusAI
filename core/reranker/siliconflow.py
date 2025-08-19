from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Union

import httpx

from langchain_core.callbacks.manager import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document
from langchain_core.utils import secret_from_env
from pydantic import ConfigDict, Field, SecretStr, model_validator
from typing_extensions import Self


class SiliconFlowReranker(BaseDocumentCompressor):
    """Document compressor that uses `SiliconFlow Rerank API`."""

    top_n: Optional[int] = 3
    """Number of documents to return."""
    base_url: Optional[str] = "https://api.siliconflow.cn/v1/rerank"
    """SiliconFlow rerank API base URL."""
    model: str
    """Model to use for reranking. Mandatory to specify the model name."""
    api_key: SecretStr
    """SiliconFlow API key. Must be specified directly."""

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_tokens: int = 0

    def rerank(
        self,
        documents: Sequence[Document],
        query: str
    ) -> List[Dict[str, Any]]:
        """Returns an ordered list of documents ordered by their relevance to the provided query.

        Args:
            documents: A sequence of documents to rerank.
            query: The query to use for reranking.
        """  # noqa: E501
        if len(documents) == 0:  # to avoid empty api call
            return []
        docs = [doc.page_content for doc in documents]
        payload = {
            "model": self.model,
            "query": query,
            "documents": docs,
            "top_n": self.top_n
        }
        headers = {
            "Authorization": f"Bearer {self.api_key.get_secret_value()}",
            "Content-Type": "application/json"
        }
        response = httpx.post(self.base_url, json=payload, headers=headers).json()
        result_dicts = []
        for res in response["results"]:
            result_dicts.append(
                {"index": res["index"], "relevance_score": res["relevance_score"]}
            )
        self.num_tokens += (response["meta"]["tokens"]["input_tokens"] + response["meta"]["tokens"]["output_tokens"])
        return result_dicts

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Compress documents using SiliconFlow's rerank API.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        compressed = []
        for res in self.rerank(documents, query):
            doc = documents[res["index"]]
            doc_copy = Document(doc.page_content, metadata=deepcopy(doc.metadata))
            doc_copy.metadata["relevance_score"] = res["relevance_score"]
            compressed.append(doc_copy)
        return compressed
