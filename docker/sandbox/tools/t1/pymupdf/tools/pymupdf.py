import logging
from collections.abc import Generator
from typing import Any
import io

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ToolParameters(BaseModel):
    files: list[File]


class PymupdfTool(Tool):
    """
    A tool for extracting text from PDF files using PyMuPDF
    """

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        if tool_parameters.get("files") is None:
            yield self.create_text_message("No files provided. Please upload PDF files for processing.")
            return
            
        params = ToolParameters(**tool_parameters)
        files = params.files

        try:
            # Try both import methods to ensure compatibility
            try:
                import pymupdf
                fitz_module = pymupdf
            except ImportError:
                import fitz
                fitz_module = fitz
                
            for file in files:
                try:
                    logger.info(f"Processing file: {file.filename}")
                    
                    # Process PDF file
                    file_bytes = io.BytesIO(file.blob)
                    doc = fitz_module.open(stream=file_bytes, filetype="pdf")
                    
                    page_count = doc.page_count
                    documents = []
                    
                    for page_num in range(page_count):
                        page = doc.load_page(page_num)
                        text = page.get_text()
                        documents.append({
                            "text": text,
                            "metadata": {
                                "page": page_num + 1,
                                "file_name": file.filename
                            }
                        })
                    
                    # Close the document to free resources
                    doc.close()
                    
                    # Join all extracted text with page separators
                    texts = "\n\n---PAGE BREAK---\n\n".join([doc["text"] for doc in documents])
                    
                    # Yield text message for human readability
                    yield self.create_text_message(texts)
                    
                    # Yield structured JSON data
                    yield self.create_json_message({file.filename: documents})
                    
                    # Yield raw text as blob with mime type
                    yield self.create_blob_message(
                        texts.encode(),
                        meta={
                            "mime_type": "text/plain",
                        },
                    )
                    
                except Exception as e:
                    error_msg = f"Error processing {file.filename}: {str(e)}"
                    logger.error(error_msg)
                    yield self.create_text_message(error_msg)
                    yield self.create_json_message({
                        file.filename: {"error": str(e)}
                    })
                    
        except ImportError as e:
            error_msg = f"Error: PyMuPDF library not installed. {str(e)}"
            logger.error(error_msg)
            yield self.create_text_message(error_msg)
