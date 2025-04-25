import os
from typing import AsyncIterator, Iterator, List, Optional

from langchain_community import document_loaders
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import TextSplitter

from languages import get_language_content

class GeneralDocumentLoader(BaseLoader):
    file_type_to_document_loader_type = {
        'csv': 'CSVLoader',
        'doc': 'UnstructuredWordDocumentLoader',
        'docx': 'Docx2txtLoader',
        'htm': 'BSHTMLLoader',
        'html': 'BSHTMLLoader',
        'jpg': 'UnstructuredImageLoader',
        'jpeg': 'UnstructuredImageLoader',
        'md': 'UnstructuredMarkdownLoader',
        'pdf': 'PyPDFLoader',
        'png': 'UnstructuredImageLoader',
        'py': 'PythonLoader',
        'rtf': 'UnstructuredRTFLoader',
        'srt': 'SRTLoader',
        'txt': 'TextLoader',
        'xls': 'UnstructuredExcelLoader',
        'xlsx': 'UnstructuredExcelLoader',
        'xml': 'UnstructuredXMLLoader'
    }
    
    def __init__(self, document_loader_type: Optional[str] = None, *args, **kwargs) -> None:
        if document_loader_type is None and 'file_path' in kwargs:
            file_path: str = kwargs['file_path']
            file_type = file_path.split('.')[-1]
            if file_type in self.file_type_to_document_loader_type:
                document_loader_type = self.file_type_to_document_loader_type[file_type]
        assert document_loader_type, get_language_content('api_vector_document_loader_type')
        if document_loader_type == 'UnstructuredImageLoader':
            kwargs['languages'] = ['eng', 'chi_sim', 'chi_sim_vert']
        document_loader_class = getattr(document_loaders, document_loader_type)
        self._document_loader: BaseLoader = document_loader_class(*args, **kwargs)
        
    def load(self) -> List[Document]:
        """Load data into Document objects."""
        return self._document_loader.load()

    async def aload(self) -> List[Document]:
        """Load data into Document objects."""
        return await self._document_loader.load()

    def load_and_split(
        self, text_splitter: Optional[TextSplitter] = None
    ) -> List[Document]:
        """Load Documents and split into chunks. Chunks are returned as Documents.

        Do not override this method. It should be considered to be deprecated!

        Args:
            text_splitter: TextSplitter instance to use for splitting documents.
              Defaults to RecursiveCharacterTextSplitter.

        Returns:
            List of Documents.
        """
        return self._document_loader.load_and_split(
            text_splitter=text_splitter
        )

    def lazy_load(self) -> Iterator[Document]:
        """A lazy loader for Documents."""
        return self._document_loader.lazy_load()

    async def alazy_load(self) -> AsyncIterator[Document]:
        """A lazy loader for Documents."""
        return await self._document_loader.alazy_load()
    