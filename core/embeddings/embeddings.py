import importlib

from typing import List

from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage.encoder_backed import EncoderBackedStore
from langchain_community import embeddings
from langchain_community.storage import RedisStore
from langchain_core.embeddings import Embeddings

from core.database import redis

_module_lookup = {
    'BaichuanTextEmbeddings': 'core.embeddings.baichuan',
    'OpenAIEmbeddings': 'core.embeddings.openai',
    'Text2vecEmbeddings': 'core.embeddings.text2vec'
}


class GeneralEmbeddings(Embeddings):
    def __init__(self, embeddings_type: str, *args, **kwargs) -> None:
        if module_name := _module_lookup.get(embeddings_type):
            module = importlib.import_module(module_name)
            embeddings_class = getattr(module, embeddings_type)
        else:
            embeddings_class = getattr(embeddings, embeddings_type)
        self._underlying_embeddings = embeddings_class(*args, **kwargs)
        match embeddings_type:
            case 'OpenAIEmbeddings':
                namespace = kwargs['model']
            case 'Text2vecEmbeddings':
                namespace = kwargs['model_name_or_path']
            case _:
                namespace = embeddings_type
        store = RedisStore(client=redis)
        self._embeddings = CacheBackedEmbeddings.from_bytes_store(
            self._underlying_embeddings, store, namespace=namespace
        )

    @property
    def document_embedding_store(self) -> EncoderBackedStore:
        """Access the store to use for caching document embeddings."""
        return self._embeddings.document_embedding_store
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed search docs."""
        return self._embeddings.embed_documents(
            texts=texts
        )

    def embed_query(self, text: str) -> List[float]:
        """Embed query text."""
        return self._embeddings.embed_query(
            text=text
        )

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Asynchronous Embed search docs."""
        return await self._embeddings.aembed_documents(
            texts=texts
        )

    async def aembed_query(self, text: str) -> List[float]:
        """Asynchronous Embed query text."""
        return await self._embeddings.aembed_query(
            text=text
        )
        
    def get_and_reset_num_tokens(self) -> int:
        if hasattr(self._underlying_embeddings, 'num_tokens'):
            num_tokens = self._underlying_embeddings.num_tokens
            self._underlying_embeddings.num_tokens = 0
            return num_tokens
        return 0
