from typing import cast, List, Optional

from langchain_core.pydantic_v1 import Extra
from langchain_openai import OpenAIEmbeddings as OriginalOpenAIEmbeddings
from langchain_openai.embeddings.base import _process_batched_chunked_embeddings


class OpenAIEmbeddings(OriginalOpenAIEmbeddings):
    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_tokens: int = 0

    # please refer to
    # https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
    def _get_len_safe_embeddings(
        self, texts: List[str], *, engine: str, chunk_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Generate length-safe embeddings for a list of texts.

        This method handles tokenization and embedding generation, respecting the
        set embedding context length and chunk size. It supports both tiktoken
        and HuggingFace tokenizer based on the tiktoken_enabled flag.

        Args:
            texts (List[str]): A list of texts to embed.
            engine (str): The engine or model to use for embeddings.
            chunk_size (Optional[int]): The size of chunks for processing embeddings.

        Returns:
            List[List[float]]: A list of embeddings for each input text.
        """
        _chunk_size = chunk_size or self.chunk_size
        _iter, tokens, indices = self._tokenize(texts, _chunk_size)
        batched_embeddings: List[List[float]] = []
        for i in _iter:
            response = self.client.create(
                input=tokens[i : i + _chunk_size], **self._invocation_params
            )
            if not isinstance(response, dict):
                response = response.model_dump()
            self.num_tokens += response["usage"]["total_tokens"]
            batched_embeddings.extend(r["embedding"] for r in response["data"])

        embeddings = _process_batched_chunked_embeddings(
            len(texts), tokens, batched_embeddings, indices, self.skip_empty
        )
        _cached_empty_embedding: Optional[List[float]] = None

        def empty_embedding() -> List[float]:
            nonlocal _cached_empty_embedding
            if _cached_empty_embedding is None:
                average_embedded = self.client.create(
                    input="", **self._invocation_params
                )
                if not isinstance(average_embedded, dict):
                    average_embedded = average_embedded.model_dump()
                _cached_empty_embedding = average_embedded["data"][0]["embedding"]
            return _cached_empty_embedding

        return [e if e is not None else empty_embedding() for e in embeddings]

    # please refer to
    # https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
    async def _aget_len_safe_embeddings(
        self, texts: List[str], *, engine: str, chunk_size: Optional[int] = None
    ) -> List[List[float]]:
        """
        Asynchronously generate length-safe embeddings for a list of texts.

        This method handles tokenization and asynchronous embedding generation,
        respecting the set embedding context length and chunk size. It supports both
        `tiktoken` and HuggingFace `tokenizer` based on the tiktoken_enabled flag.

        Args:
            texts (List[str]): A list of texts to embed.
            engine (str): The engine or model to use for embeddings.
            chunk_size (Optional[int]): The size of chunks for processing embeddings.

        Returns:
            List[List[float]]: A list of embeddings for each input text.
        """

        _chunk_size = chunk_size or self.chunk_size
        _iter, tokens, indices = self._tokenize(texts, _chunk_size)
        batched_embeddings: List[List[float]] = []
        _chunk_size = chunk_size or self.chunk_size
        for i in range(0, len(tokens), _chunk_size):
            response = await self.async_client.create(
                input=tokens[i : i + _chunk_size], **self._invocation_params
            )

            if not isinstance(response, dict):
                response = response.model_dump()
            self.num_tokens += response["usage"]["total_tokens"]
            batched_embeddings.extend(r["embedding"] for r in response["data"])

        embeddings = _process_batched_chunked_embeddings(
            len(texts), tokens, batched_embeddings, indices, self.skip_empty
        )
        _cached_empty_embedding: Optional[List[float]] = None

        async def empty_embedding() -> List[float]:
            nonlocal _cached_empty_embedding
            if _cached_empty_embedding is None:
                average_embedded = await self.async_client.create(
                    input="", **self._invocation_params
                )
                if not isinstance(average_embedded, dict):
                    average_embedded = average_embedded.model_dump()
                _cached_empty_embedding = average_embedded["data"][0]["embedding"]
            return _cached_empty_embedding

        return [e if e is not None else await empty_embedding() for e in embeddings]
    
    def embed_documents(
        self, texts: List[str], chunk_size: Optional[int] = 0
    ) -> List[List[float]]:
        """Call out to OpenAI's embedding endpoint for embedding search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings. If None, will use the chunk size
                specified by the class.

        Returns:
            List of embeddings, one for each text.
        """
        if not self.check_embedding_ctx_length:
            embeddings: List[List[float]] = []
            for text in texts:
                response = self.client.create(input=text, **self._invocation_params)
                if not isinstance(response, dict):
                    response = response.dict()
                self.num_tokens += response["usage"]["total_tokens"]
                embeddings.extend(r["embedding"] for r in response["data"])
            return embeddings

        # NOTE: to keep things simple, we assume the list may contain texts longer
        #       than the maximum context and use length-safe embedding function.
        engine = cast(str, self.deployment)
        return self._get_len_safe_embeddings(texts, engine=engine)
    
    async def aembed_documents(
        self, texts: List[str], chunk_size: Optional[int] = 0
    ) -> List[List[float]]:
        """Call out to OpenAI's embedding endpoint async for embedding search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings. If None, will use the chunk size
                specified by the class.

        Returns:
            List of embeddings, one for each text.
        """
        if not self.check_embedding_ctx_length:
            embeddings: List[List[float]] = []
            for text in texts:
                response = await self.async_client.create(
                    input=text, **self._invocation_params
                )
                if not isinstance(response, dict):
                    response = response.dict()
                self.num_tokens += response["usage"]["total_tokens"]
                embeddings.extend(r["embedding"] for r in response["data"])
            return embeddings

        # NOTE: to keep things simple, we assume the list may contain texts longer
        #       than the maximum context and use length-safe embedding function.
        engine = cast(str, self.deployment)
        return await self._aget_len_safe_embeddings(texts, engine=engine)
    