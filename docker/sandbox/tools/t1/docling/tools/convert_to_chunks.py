from collections.abc import Generator
from typing import Any,List

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from docling.document_converter import DocumentConverter
from .utils import DifyDocling
import tempfile

class DoclingConvertChunks(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        files = tool_parameters.get('files', [])
        if not files:
            yield self.create_text_message("No files provided for conversion.")
            return
        temp_file_paths= []
        for file in files:
            file_extension = file.extension if file.extension else '.tmp'
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(file.blob)
                temp_file_path = temp_file.name
                temp_file_paths.append(temp_file_path)
        docling = DifyDocling()
        docling_documents = docling.documents_to_markdown(temp_file_paths)
        chunked_results = docling.docling_document_to_chunks(docling_documents)
        return_results = {}
        for idx,chunked_result in enumerate(chunked_results):
            return_results[files[idx].filename]=chunked_results[chunked_result]
            
        yield self.create_json_message(return_results)
        

