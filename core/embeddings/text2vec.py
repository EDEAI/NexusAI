from typing import List

from langchain_community.embeddings.text2vec import Text2vecEmbeddings as OriginalText2vecEmbeddings
from langchain_core.pydantic_v1 import Extra
from numpy import ndarray


class Text2vecEmbeddings(OriginalText2vecEmbeddings):
    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using the text2vec embeddings model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        result = self.model.encode(texts, normalize_embeddings=True)
        if isinstance(result, ndarray):
            result = result.tolist()
        return result
    

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using the text2vec embeddings model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        result = self.model.encode(text, normalize_embeddings=True)
        if isinstance(result, ndarray):
            result = result.tolist()
        return result
    