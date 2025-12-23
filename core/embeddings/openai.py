from typing import Any, Literal, cast


from langchain_openai import OpenAIEmbeddings as OriginalOpenAIEmbeddings
from langchain_openai.embeddings.base import _process_batched_chunked_embeddings

MAX_TOKENS_PER_REQUEST = 300000
"""API limit per request for embedding tokens."""


class OpenAIEmbeddings(OriginalOpenAIEmbeddings):
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_tokens: int = 0

    # please refer to
    # https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
    def _get_len_safe_embeddings(
        self,
        texts: list[str],
        *,
        engine: str,
        chunk_size: int | None = None,
        **kwargs: Any,
    ) -> list[list[float]]:
        """Generate length-safe embeddings for a list of texts.

        This method handles tokenization and embedding generation, respecting the
        `embedding_ctx_length` and `chunk_size`. Supports both `tiktoken` and
        HuggingFace `transformers` based on the `tiktoken_enabled` flag.

        Args:
            texts: The list of texts to embed.
            engine: The engine or model to use for embeddings.
            chunk_size: The size of chunks for processing embeddings.

        Returns:
            A list of embeddings for each input text.
        """
        _chunk_size = chunk_size or self.chunk_size
        client_kwargs = {**self._invocation_params, **kwargs}
        _iter, tokens, indices, token_counts = self._tokenize(texts, _chunk_size)
        batched_embeddings: list[list[float]] = []

        # Process in batches respecting the token limit
        i = 0
        while i < len(tokens):
            # Determine how many chunks we can include in this batch
            batch_token_count = 0
            batch_end = i

            for j in range(i, min(i + _chunk_size, len(tokens))):
                chunk_tokens = token_counts[j]
                # Check if adding this chunk would exceed the limit
                if batch_token_count + chunk_tokens > MAX_TOKENS_PER_REQUEST:
                    if batch_end == i:
                        # Single chunk exceeds limit - handle it anyway
                        batch_end = j + 1
                    break
                batch_token_count += chunk_tokens
                batch_end = j + 1

            # Make API call with this batch
            batch_tokens = tokens[i:batch_end]
            response = self.client.create(input=batch_tokens, **client_kwargs)
            if not isinstance(response, dict):
                response = response.model_dump()
            self.num_tokens += response["usage"]["total_tokens"]
            batched_embeddings.extend(r["embedding"] for r in response["data"])

            i = batch_end

        embeddings = _process_batched_chunked_embeddings(
            len(texts), tokens, batched_embeddings, indices, self.skip_empty
        )
        _cached_empty_embedding: list[float] | None = None

        def empty_embedding() -> list[float]:
            nonlocal _cached_empty_embedding
            if _cached_empty_embedding is None:
                average_embedded = self.client.create(input="", **client_kwargs)
                if not isinstance(average_embedded, dict):
                    average_embedded = average_embedded.model_dump()
                _cached_empty_embedding = average_embedded["data"][0]["embedding"]
            return _cached_empty_embedding

        return [e if e is not None else empty_embedding() for e in embeddings]

    # please refer to
    # https://github.com/openai/openai-cookbook/blob/main/examples/Embedding_long_inputs.ipynb
    async def _aget_len_safe_embeddings(
        self,
        texts: list[str],
        *,
        engine: str,
        chunk_size: int | None = None,
        **kwargs: Any,
    ) -> list[list[float]]:
        """Asynchronously generate length-safe embeddings for a list of texts.

        This method handles tokenization and embedding generation, respecting the
        `embedding_ctx_length` and `chunk_size`. Supports both `tiktoken` and
        HuggingFace `transformers` based on the `tiktoken_enabled` flag.

        Args:
            texts: The list of texts to embed.
            engine: The engine or model to use for embeddings.
            chunk_size: The size of chunks for processing embeddings.

        Returns:
            A list of embeddings for each input text.
        """
        _chunk_size = chunk_size or self.chunk_size
        client_kwargs = {**self._invocation_params, **kwargs}
        _iter, tokens, indices, token_counts = await run_in_executor(
            None, self._tokenize, texts, _chunk_size
        )
        batched_embeddings: list[list[float]] = []

        # Process in batches respecting the token limit
        i = 0
        while i < len(tokens):
            # Determine how many chunks we can include in this batch
            batch_token_count = 0
            batch_end = i

            for j in range(i, min(i + _chunk_size, len(tokens))):
                chunk_tokens = token_counts[j]
                # Check if adding this chunk would exceed the limit
                if batch_token_count + chunk_tokens > MAX_TOKENS_PER_REQUEST:
                    if batch_end == i:
                        # Single chunk exceeds limit - handle it anyway
                        batch_end = j + 1
                    break
                batch_token_count += chunk_tokens
                batch_end = j + 1

            # Make API call with this batch
            batch_tokens = tokens[i:batch_end]
            response = await self.async_client.create(
                input=batch_tokens, **client_kwargs
            )
            if not isinstance(response, dict):
                response = response.model_dump()
            self.num_tokens += response["usage"]["total_tokens"]
            batched_embeddings.extend(r["embedding"] for r in response["data"])

            i = batch_end

        embeddings = _process_batched_chunked_embeddings(
            len(texts), tokens, batched_embeddings, indices, self.skip_empty
        )
        _cached_empty_embedding: list[float] | None = None

        async def empty_embedding() -> list[float]:
            nonlocal _cached_empty_embedding
            if _cached_empty_embedding is None:
                average_embedded = await self.async_client.create(
                    input="", **client_kwargs
                )
                if not isinstance(average_embedded, dict):
                    average_embedded = average_embedded.model_dump()
                _cached_empty_embedding = average_embedded["data"][0]["embedding"]
            return _cached_empty_embedding

        return [e if e is not None else await empty_embedding() for e in embeddings]

    def embed_documents(
        self, texts: list[str], chunk_size: int | None = None, **kwargs: Any
    ) -> list[list[float]]:
        """Call OpenAI's embedding endpoint to embed search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings.

                If `None`, will use the chunk size specified by the class.
            kwargs: Additional keyword arguments to pass to the embedding API.

        Returns:
            List of embeddings, one for each text.
        """
        self._ensure_sync_client_available()
        chunk_size_ = chunk_size or self.chunk_size
        client_kwargs = {**self._invocation_params, **kwargs}
        if not self.check_embedding_ctx_length:
            embeddings: list[list[float]] = []
            for i in range(0, len(texts), chunk_size_):
                response = self.client.create(
                    input=texts[i : i + chunk_size_], **client_kwargs
                )
                if not isinstance(response, dict):
                    response = response.model_dump()
                self.num_tokens += response["usage"]["total_tokens"]
                embeddings.extend(r["embedding"] for r in response["data"])
            return embeddings

        # Unconditionally call _get_len_safe_embeddings to handle length safety.
        # This could be optimized to avoid double work when all texts are short enough.
        engine = cast(str, self.deployment)
        return self._get_len_safe_embeddings(
            texts, engine=engine, chunk_size=chunk_size, **kwargs
        )

    async def aembed_documents(
        self, texts: list[str], chunk_size: int | None = None, **kwargs: Any
    ) -> list[list[float]]:
        """Asynchronously call OpenAI's embedding endpoint to embed search docs.

        Args:
            texts: The list of texts to embed.
            chunk_size: The chunk size of embeddings.

                If `None`, will use the chunk size specified by the class.
            kwargs: Additional keyword arguments to pass to the embedding API.

        Returns:
            List of embeddings, one for each text.
        """
        chunk_size_ = chunk_size or self.chunk_size
        client_kwargs = {**self._invocation_params, **kwargs}
        if not self.check_embedding_ctx_length:
            embeddings: list[list[float]] = []
            for i in range(0, len(texts), chunk_size_):
                response = await self.async_client.create(
                    input=texts[i : i + chunk_size_], **client_kwargs
                )
                if not isinstance(response, dict):
                    response = response.model_dump()
                self.num_tokens += response["usage"]["total_tokens"]
                embeddings.extend(r["embedding"] for r in response["data"])
            return embeddings

        # Unconditionally call _get_len_safe_embeddings to handle length safety.
        # This could be optimized to avoid double work when all texts are short enough.
        engine = cast(str, self.deployment)
        return await self._aget_len_safe_embeddings(
            texts, engine=engine, chunk_size=chunk_size, **kwargs
        )
