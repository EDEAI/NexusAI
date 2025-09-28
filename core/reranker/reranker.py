import importlib

from typing import List, Optional, Sequence

from langchain.retrievers import document_compressors
from langchain.retrievers.document_compressors.cross_encoder import BaseCrossEncoder
from langchain_community import cross_encoders
from langchain_community import document_compressors as lcc_document_compressors
from langchain_core.callbacks import Callbacks
from langchain_core.documents import BaseDocumentCompressor, Document

_module_lookup = {
    'CrossEncoderReranker': 'core.reranker.cross_encoder_rerank',
    'SiliconFlowReranker': 'core.reranker.siliconflow',
    'Qwen3CrossEncoder': 'core.reranker.qwen3',
}


class GeneralReranker(BaseDocumentCompressor):
    model_config = {
        "extra": "allow",
        "arbitrary_types_allowed": True,
    }
    
    def __init__(self, reranker_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if module_name := _module_lookup.get(reranker_type):
            module = importlib.import_module(module_name)
            reranker_class = getattr(module, reranker_type)
        else:
            reranker_class = getattr(document_compressors, reranker_type, None)
            if reranker_class is None:
                reranker_class = getattr(lcc_document_compressors, reranker_type)
        match reranker_type:
            case 'CrossEncoderReranker':
                model_type = kwargs.pop('model_type')
                model_kwargs = kwargs.pop('model_kwargs')
                if module_name := _module_lookup.get(model_type):
                    module = importlib.import_module(module_name)
                    model_class = getattr(module, model_type)
                else:
                    model_class = getattr(cross_encoders, model_type)
                model: BaseCrossEncoder = model_class(**model_kwargs)
                self._reranker: BaseDocumentCompressor = reranker_class(model=model, *args, **kwargs)
            case _:
                self._reranker: BaseDocumentCompressor = reranker_class(*args, **kwargs)
        
    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Compress retrieved documents given the query context."""
        return self._reranker.compress_documents(
            documents=documents,
            query=query,
            callbacks=callbacks
        )

    async def acompress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """Compress retrieved documents given the query context."""
        return await self._reranker.acompress_documents(
            documents=documents,
            query=query,
            callbacks=callbacks
        )
        
    def get_and_reset_num_tokens(self) -> int:
        if hasattr(self._reranker, 'num_tokens'):
            num_tokens = self._reranker.num_tokens
            self._reranker.num_tokens = 0
            return num_tokens
        return 0
    