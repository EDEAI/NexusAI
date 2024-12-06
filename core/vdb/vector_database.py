import importlib

from enum import IntEnum
from typing import (
    Any,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
)

from langchain_community import vectorstores
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever

VST = TypeVar('VST', bound='VectorStore')

_module_lookup = {
    'Milvus': 'core.vdb.milvus'
}


class DeleteDatasetStatus(IntEnum):
    OK = 0
    ERROR = 1
    NOT_SUPPORTED = 2

class GeneralVectorDatabase(VectorStore):
    def __init__(self, vector_type: str, *args, **kwargs) -> None:
        self._vector_type = vector_type
        if module_name := _module_lookup.get(vector_type):
            module = importlib.import_module(module_name)
            vector_class = getattr(module, vector_type)
        else:
            vector_class = getattr(vectorstores, vector_type)
        self._vector_store: VectorStore = vector_class(*args, **kwargs)

    def _generate_filter(self, documents: Optional[List[str]] = None) -> Optional[Tuple[str, Any]]:
        if self._vector_type == 'Milvus':
            if documents:
                import json
                return 'expr', f'source in {json.dumps(documents, ensure_ascii=False)}'

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            **kwargs: vectorstore specific parameters.

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        return [str(id_) for id_ in self._vector_store.add_texts(
            texts=texts,
            metadatas=metadatas,
            **kwargs
        )]

    @property
    def embeddings(self) -> Optional[Embeddings]:
        """Access the query embedding object if available."""
        return self._vector_store.embeddings

    def delete(self, ids: Optional[List[str]] = None, **kwargs: Any) -> Optional[bool]:
        """Delete by vector ID or other criteria.

        Args:
            ids: List of ids to delete.
            **kwargs: Other keyword arguments that subclasses might use.
  
        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise, None if not implemented.
        """
        return self._vector_store.delete(
            ids=ids,
            **kwargs
        )

    async def adelete(
        self, ids: Optional[List[str]] = None, **kwargs: Any
    ) -> Optional[bool]:
        """Delete by vector ID or other criteria.

        Args:
            ids: List of ids to delete.
            **kwargs: Other keyword arguments that subclasses might use.

        Returns:
            Optional[bool]: True if deletion is successful,
            False otherwise, None if not implemented.
        """
        return await self._vector_store.adelete(
            ids,
            **kwargs
        )

    async def aadd_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts: Iterable of strings to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            **kwargs: vectorstore specific parameters.

        Returns:
            List of ids from adding the texts into the vectorstore.
        """
        return [str(id_) for id_ in await self._vector_store.aadd_texts(
            texts=texts,
            metadatas=metadatas,
            **kwargs
        )]

    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents: Documents to add to the vectorstore.

        Returns:
            List of IDs of the added texts.
        """
        return [str(id_) for id_ in self._vector_store.add_documents(
            documents=documents,
            **kwargs
        )]

    async def aadd_documents(
        self, documents: List[Document], **kwargs: Any
    ) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents: Documents to add to the vectorstore.

        Returns:
            List of IDs of the added texts.
        """
        return [str(id_) for id_ in await self._vector_store.aadd_documents(
            documents=documents,
            **kwargs
        )]

    def search(
        self,
        query: str,
        search_type: str,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query using specified search type.

        Args:
            query: Input text
            search_type: Type of search to perform. Can be "similarity",
                "mmr", or "similarity_score_threshold".
            search_in_documents: Optional list of document names to search in.
            **kwargs: Arguments to pass to the search method.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.search(
            query=query,
            search_type=search_type,
            **kwargs
        )

    async def asearch(
        self,
        query: str,
        search_type: str,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query using specified search type.

        Args:
            query: Input text.
            search_type: Type of search to perform. Can be "similarity",
                "mmr", or "similarity_score_threshold".
            search_in_documents: Optional list of document names to search in.
            **kwargs: Arguments to pass to the search method.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.asearch(
            query=query,
            search_type=search_type,
            **kwargs
        )

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query.

        Args:
            query: Input text.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.

        Returns:
            List of Documents most similar to the query.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.similarity_search(
            query=query,
            k=k,
            **kwargs
        )

    def similarity_search_with_score(
        self,
        search_in_documents: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """Run similarity search with distance.

        Returns:
            List of Tuples of (doc, similarity_score)
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.similarity_search_with_score(
            *args,
            **kwargs
        )

    async def asimilarity_search_with_score(
        self,
        search_in_documents: Optional[List[str]] = None,
        *args: Any,
        **kwargs: Any
    ) -> List[Tuple[Document, float]]:
        """Run similarity search with distance.

        Returns:
            List of Tuples of (doc, similarity_score)
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.asimilarity_search_with_score(
            *args,
            **kwargs
        )

    def similarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return docs and relevance scores in the range [0, 1].

        0 is dissimilar, 1 is most similar.

        Args:
            query: Input text.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.
            **kwargs: kwargs to be passed to similarity search. Should include:
                score_threshold: Optional, a floating point value between 0 to 1 to
                    filter the resulting set of retrieved docs

        Returns:
            List of Tuples of (doc, similarity_score)
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=k,
            **kwargs
        )

    async def asimilarity_search_with_relevance_scores(
        self,
        query: str,
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Return docs and relevance scores in the range [0, 1].

        0 is dissimilar, 1 is most similar.

        Args:
            query: Input text.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.
            **kwargs: kwargs to be passed to similarity search. Should include:
                score_threshold: Optional, a floating point value between 0 to 1 to
                    filter the resulting set of retrieved docs

        Returns:
            List of Tuples of (doc, similarity_score)
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.asimilarity_search_with_relevance_scores(
            query=query,
            k=k,
            **kwargs
        )

    async def asimilarity_search(
        self,
        query: str,
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to query.

        Args:
            query: Input text.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents most similar to the query.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.asimilarity_search(
            query=query,
            k=k,
            **kwargs
        )

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to embedding vector.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents most similar to the query vector.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.similarity_search_by_vector(
            embedding=embedding,
            k=k,
            **kwargs
        )

    async def asimilarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any
    ) -> List[Document]:
        """Return docs most similar to embedding vector.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents most similar to the query vector.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.asimilarity_search_by_vector(
            embedding=embedding,
            k=k,
            **kwargs
        )

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.max_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            **kwargs
        )

    async def amax_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            query: Text to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.amax_marginal_relevance_search(
            query=query,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            **kwargs
        )

    def max_marginal_relevance_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return self._vector_store.max_marginal_relevance_search_by_vector(
            embedding=embedding,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            **kwargs
        )

    async def amax_marginal_relevance_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        search_in_documents: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Return docs selected using the maximal marginal relevance.

        Maximal marginal relevance optimizes for similarity to query AND diversity
        among selected documents.

        Args:
            embedding: Embedding to look up documents similar to.
            k: Number of Documents to return. Defaults to 4.
            fetch_k: Number of Documents to fetch to pass to MMR algorithm.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5.
            search_in_documents: Optional list of document names to search in.
        Returns:
            List of Documents selected by maximal marginal relevance.
        """
        if search_in_documents and (key_value := self._generate_filter(search_in_documents)):
            key, value = key_value
            kwargs[key] = value
        return await self._vector_store.amax_marginal_relevance_search_by_vector(
            embedding=embedding,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            **kwargs
        )

    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embedding: Embeddings,
        *,
        vector_type: str,
        **kwargs: Any,
    ) -> VST:
        """Return VectorStore initialized from documents and embeddings.

        Args:
            documents: List of Documents to add to the vectorstore.
            embedding: Embedding function to use.
        """
        vector_class = getattr(vectorstores, vector_type)
        return vector_class.from_documents(
            documents=documents,
            embedding=embedding,
            **kwargs
        )

    @classmethod
    async def afrom_documents(
        self,
        documents: List[Document],
        embedding: Embeddings,
        *,
        vector_type: str,
        **kwargs: Any,
    ) -> VST:
        """Return VectorStore initialized from documents and embeddings.

        Args:
            documents: List of Documents to add to the vectorstore.
            embedding: Embedding function to use.
        """
        vector_class = getattr(vectorstores, vector_type)
        return await vector_class.afrom_documents(
            documents=documents,
            embedding=embedding,
            **kwargs
        )

    @classmethod
    def from_texts(
        self,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        *,
        vector_type: str,
        **kwargs: Any,
    ) -> VST:
        """Return VectorStore initialized from texts and embeddings.

        Args:
            texts: Texts to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            embedding: Embedding function to use.
        """
        vector_class = getattr(vectorstores, vector_type)
        return vector_class.from_documents(
            texts=texts,
            embedding=embedding,
            metadatas=metadatas,
            **kwargs
        )

    @classmethod
    async def afrom_texts(
        self,
        texts: List[str],
        embedding: Embeddings,
        metadatas: Optional[List[dict]] = None,
        *,
        vector_type: str,
        **kwargs: Any,
    ) -> VST:
        """Return VectorStore initialized from texts and embeddings.

        Args:
            texts: Texts to add to the vectorstore.
            metadatas: Optional list of metadatas associated with the texts.
            embedding: Embedding function to use.
        """
        vector_class = getattr(vectorstores, vector_type)
        return await vector_class.afrom_documents(
            texts=texts,
            embedding=embedding,
            metadatas=metadatas,
            **kwargs
        )

    def as_retriever(self, **kwargs: Any) -> VectorStoreRetriever:
        """Return VectorStoreRetriever initialized from this VectorStore.

        Args:
            search_type (Optional[str]): Defines the type of search that
                the Retriever should perform.
                Can be "similarity" (default), "mmr", or
                "similarity_score_threshold".
            search_kwargs (Optional[Dict]): Keyword arguments to pass to the
                search function. Can include things like:
                    k: Amount of documents to return (Default: 4)
                    score_threshold: Minimum relevance threshold
                        for similarity_score_threshold
                    fetch_k: Amount of documents to pass to MMR algorithm (Default: 20)
                    lambda_mult: Diversity of results returned by MMR;
                        1 for minimum diversity and 0 for maximum. (Default: 0.5)
                    filter: Filter by document metadata

        Returns:
            VectorStoreRetriever: Retriever class for VectorStore.

        Examples:

        .. code-block:: python

            # Retrieve more documents with higher diversity
            # Useful if your dataset has many similar documents
            docsearch.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 6, 'lambda_mult': 0.25}
            )

            # Fetch more documents for the MMR algorithm to consider
            # But only return the top 5
            docsearch.as_retriever(
                search_type="mmr",
                search_kwargs={'k': 5, 'fetch_k': 50}
            )

            # Only retrieve documents that have a relevance score
            # Above a certain threshold
            docsearch.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={'score_threshold': 0.8}
            )

            # Only get the single most similar document from the dataset
            docsearch.as_retriever(search_kwargs={'k': 1})

            # Use a filter to only retrieve documents from a specific paper
            docsearch.as_retriever(
                search_kwargs={'filter': {'paper_title':'GPT-4 Technical Report'}}
            )
        """
        return self._vector_store.as_retriever(**kwargs)
    
    def delete_dataset(self) -> DeleteDatasetStatus:
        if delete_dataset_func := getattr(self._vector_store, 'delete_dataset', None):
            return (
                DeleteDatasetStatus.OK if delete_dataset_func()
                else DeleteDatasetStatus.ERROR
            )
        return DeleteDatasetStatus.NOT_SUPPORTED
