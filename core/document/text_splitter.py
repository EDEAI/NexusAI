from typing import Any, Iterable, List, Optional, Sequence

import langchain_text_splitters

from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter


class GeneralTextSplitter(TextSplitter):
    def __init__(
        self,
        text_splitter_type: str = 'RecursiveCharacterTextSplitter',
        *args,
        **kwargs
    ) -> None:
        text_splitter_class = getattr(langchain_text_splitters, text_splitter_type)
        self._text_splitter: TextSplitter = text_splitter_class(*args, **kwargs)
        
    def split_text(self, text: str) -> List[str]:
        """Split text into multiple components."""
        return self._text_splitter.split_text(text=text)
    
    def create_documents(
        self, texts: List[str], metadatas: Optional[List[dict]] = None, **kwargs
    ) -> List[Document]:
        """Create documents from a list of texts."""
        return self._text_splitter.create_documents(
            texts=texts,
            metadatas=metadatas,
            **kwargs
        )
        
    def split_documents(self, documents: Iterable[Document]) -> List[Document]:
        """Split documents."""
        return self._text_splitter.split_documents(documents=documents)
    
    def transform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        """Transform sequence of documents by splitting them."""
        return self._text_splitter.transform_documents(
            documents=documents,
            **kwargs
        )

    async def atransform_documents(
        self, documents: Sequence[Document], **kwargs: Any
    ) -> Sequence[Document]:
        """Asynchronously transform a list of documents.

        Args:
            documents: A sequence of Documents to be transformed.

        Returns:
            A list of transformed Documents.
        """
        return await self._text_splitter.atransform_documents(
            documents=documents,
            **kwargs
        )
    