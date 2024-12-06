from typing import List, Optional

from langchain_community.embeddings import BaichuanTextEmbeddings as OriginalBaichuanTextEmbeddings
from langchain_core.pydantic_v1 import Extra
from requests import RequestException

BAICHUAN_API_URL: str = "http://api.baichuan-ai.com/v1/embeddings"


class BaichuanTextEmbeddings(OriginalBaichuanTextEmbeddings):
    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True
        
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_tokens: int = 0

    def _embed(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Internal method to call Baichuan Embedding API and return embeddings.

        Args:
            texts: A list of texts to embed.

        Returns:
            A list of list of floats representing the embeddings, or None if an
            error occurs.
        """
        response = self.session.post(
            BAICHUAN_API_URL, json={"input": texts, "model": self.model_name}
        )
        # Raise exception if response status code from 400 to 600
        response.raise_for_status()
        # Check if the response status code indicates success
        if response.status_code == 200:
            resp = response.json()
            self.num_tokens += resp.get("usage", {}).get("total_tokens", 0)
            embeddings = resp.get("data", [])
            # Sort resulting embeddings by index
            sorted_embeddings = sorted(embeddings, key=lambda e: e.get("index", 0))
            # Return just the embeddings
            return [result.get("embedding", []) for result in sorted_embeddings]
        else:
            # Log error or handle unsuccessful response appropriately
            # Handle 100 <= status_code < 400, not include 200
            raise RequestException(
                f"Error: Received status code {response.status_code} from "
                "`BaichuanEmbedding` API"
            )
    