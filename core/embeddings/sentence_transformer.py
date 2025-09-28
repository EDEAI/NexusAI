
from typing import List

from langchain_community.embeddings.sentence_transformer \
    import SentenceTransformerEmbeddings as OriginalSentenceTransformerEmbeddings


class SentenceTransformerEmbeddings(OriginalSentenceTransformerEmbeddings):
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Compute doc embeddings using a HuggingFace transformer model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        texts = list(map(lambda x: x.replace("\n", " "), texts))
        embeddings = self.client.encode(
            texts, show_progress_bar=self.show_progress, **self.encode_kwargs
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Compute query embeddings using a HuggingFace transformer model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        return self.embed_documents([text])[0]
    