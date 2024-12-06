from typing import Any, List, Optional

from langchain import retrievers
from langchain_community import retrievers as lcc_retrievers
from langchain_core.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun
)
from langchain_core.documents import Document
from langchain_core.pydantic_v1 import Extra
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import RunnableConfig
from langchain_core.vectorstores import VectorStore, VectorStoreRetriever


class GeneralRetriever(BaseRetriever):
    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.allow
        arbitrary_types_allowed = True
    
    def __init__(self, retriever_type: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        match retriever_type:
            case 'VectorStoreRetriever':
                vectorstore: VectorStore = kwargs.pop('vectorstore')
                tags = kwargs.pop('tags', None) or [] + vectorstore._get_retriever_tags()
                self._retriever: BaseRetriever = VectorStoreRetriever(
                    vectorstore=vectorstore,
                    tags=tags,
                    **kwargs
                )
            case _:
                retriever_class = getattr(lcc_retrievers, retriever_type, None)
                if retriever_class is None:
                    retriever_class = getattr(retrievers, retriever_type)
                self._retriever: BaseRetriever = retriever_class(*args, **kwargs)
        
    def invoke(
        self, input: str, config: Optional[RunnableConfig] = None, **kwargs: Any
    ) -> List[Document]:
        return self._retriever.invoke(
            input=input,
            config=config,
            **kwargs
        )
        
    async def ainvoke(
        self,
        input: str,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> List[Document]:
        return await self._retriever.ainvoke(
            input=input,
            config=config,
            **kwargs
        )
    
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        return self._retriever._get_relevant_documents(
            query=query,
            run_manager=run_manager
        )

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Asynchronously get documents relevant to a query.
        Args:
            query: String to find relevant documents for
            run_manager: The callbacks handler to use
        Returns:
            List of relevant documents
        """
        return await self._retriever._aget_relevant_documents(
            query=query,
            run_manager=run_manager
        )
    