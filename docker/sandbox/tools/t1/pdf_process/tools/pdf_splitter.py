import io
from collections.abc import Generator
from typing import Any, Optional, List

import PyPDF2
from dify_plugin.entities import I18nObject
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter
from dify_plugin import Tool
from dify_plugin.file.file import File

class PDFSplitterTool(Tool):
    """
    A tool for splitting PDF files into individual pages.
    This tool takes a PDF file (base64 encoded or Dify file object) as input,
    and returns all pages as separate PDF files.
    """

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Split a PDF file into individual pages.

        Args:
            tool_parameters (dict[str, Any]): Parameters for the tool
                - pdf_content (File): Dify File object containing the PDF
            user_id (Optional[str], optional): The ID of the user invoking the tool. Defaults to None.
            conversation_id (Optional[str], optional): The conversation ID. Defaults to None.
            app_id (Optional[str], optional): The app ID. Defaults to None.
            message_id (Optional[str], optional): The message ID. Defaults to None.

        Returns:
            Generator[ToolInvokeMessage, None, None]: Generator yielding the PDF pages as separate files
            
        Raises:
            ValueError: If the PDF content format is invalid or required parameters are missing
            Exception: For any other errors during PDF processing
        """
        try:
            pdf_content = tool_parameters.get("pdf_content")
            if not isinstance(pdf_content, File):
                raise ValueError("Invalid PDF content format. Expected File object.")
            
            original_filename = pdf_content.filename or "document"
            
            try:
                # Convert bytes to BytesIO object before passing to PdfReader
                pdf_bytes_io = io.BytesIO(pdf_content.blob)
                pdf_reader = PyPDF2.PdfReader(pdf_bytes_io)
            except Exception as e:
                raise ValueError(f"Invalid PDF file: {str(e)}")
            
            total_pages = len(pdf_reader.pages)
            
            if total_pages == 0:
                raise ValueError("The PDF file contains no pages.")
            
            # Prepare the base filename
            if original_filename.lower().endswith('.pdf'):
                base_filename = original_filename[:-4]
            else:
                base_filename = original_filename
            
            # First, send a text message indicating the process has started
            yield self.create_text_message(f"Splitting PDF into {total_pages} individual pages...")
            
            # Process each page
            page_files = []
            for page_idx in range(total_pages):
                # Create a new PDF with just this page
                output = PyPDF2.PdfWriter()
                output.add_page(pdf_reader.pages[page_idx])
                
                # Write to a buffer
                page_buffer = io.BytesIO()
                output.write(page_buffer)
                page_buffer.seek(0)
                
                # Create filename for this page
                output_filename = f"{base_filename}_page{page_idx + 1}.pdf"
                
                # Add to our list of files
                page_files.append({
                    "blob": page_buffer.getvalue(),
                    "meta": {
                        "mime_type": "application/pdf",
                        "file_name": output_filename
                    }
                })
            
            # Send a summary message
            yield self.create_text_message(f"Successfully split PDF into {total_pages} pages.")
            
            # Send each page as a separate blob message
            for page_file in page_files:
                yield self.create_blob_message(
                    blob=page_file["blob"],
                    meta=page_file["meta"],
                )
            
        except ValueError as e:
            raise
        except Exception as e:
            raise Exception(f"Error splitting PDF into pages: {str(e)}")
            
    def get_runtime_parameters(
        self,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> list[ToolParameter]:
        """
        Get the runtime parameters for the PDF splitter tool.
        
        Returns:
            list[ToolParameter]: List of tool parameters
        """
        parameters = [
            ToolParameter(
                name="pdf_content",
                label=I18nObject(en_US="PDF Content", zh_Hans="PDF 内容"),
                human_description=I18nObject(
                    en_US="PDF file content to split into individual pages",
                    zh_Hans="要分割成单独页面的PDF文件内容",
                ),
                type=ToolParameter.ToolParameterType.FILE,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
                file_accepts=["application/pdf"],
            ),
        ]
        return parameters
