import io
from collections.abc import Generator
from typing import Any, Optional, List

import pymupdf
from PIL import Image
from dify_plugin.entities import I18nObject
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter
from dify_plugin import Tool
from dify_plugin.file.file import File

class PDFToPNGTool(Tool):
    """
    A tool for converting PDF files to PNG images.
    This tool takes a PDF file as input and returns each page as a separate PNG image.
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
        Convert a PDF file to PNG images.

        Args:
            tool_parameters (dict[str, Any]): Parameters for the tool
                - pdf_content (File): Dify File object containing the PDF
                - zoom (float): Zoom factor for image quality (default is 2)
            user_id (Optional[str]): The ID of the user invoking the tool
            conversation_id (Optional[str]): The conversation ID
            app_id (Optional[str]): The app ID
            message_id (Optional[str]): The message ID

        Returns:
            Generator[ToolInvokeMessage, None, None]: Generator yielding the PNG images

        Raises:
            ValueError: If the PDF content format is invalid or required parameters are missing
            Exception: For any other errors during PDF processing
        """
        try:
            # Get and validate parameters
            pdf_content = tool_parameters.get("pdf_content")
            if not isinstance(pdf_content, File):
                raise ValueError("Invalid PDF content format. Expected File object.")
            
            # Get zoom parameter with default value
            zoom_param = tool_parameters.get("zoom")
            zoom = 2 if zoom_param is None else int(zoom_param)
            
            original_filename = pdf_content.filename or "document"
            base_filename = original_filename.rsplit('.', 1)[0]
            
            # Convert bytes to BytesIO object
            pdf_bytes_io = io.BytesIO(pdf_content.blob)
            
            try:
                # Open PDF with PyMuPDF
                doc = pymupdf.open(stream=pdf_bytes_io)
            except Exception as e:
                raise ValueError(f"Invalid PDF file: {str(e)}")
            
            total_pages = doc.page_count
            if total_pages == 0:
                raise ValueError("The PDF file contains no pages.")
            
            # Send initial status message
            yield self.create_text_message(f"Converting PDF with {total_pages} pages to PNG images...")
            
            # Process each page
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                mat = pymupdf.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                
                # Convert PyMuPDF pixmap to PIL Image
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                
                # Save PIL Image to an in-memory bytes buffer
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                
                # Create filename for this page
                output_filename = f"{base_filename}_page{page_num + 1}.png"
                
                # Send the PNG image
                yield self.create_blob_message(
                    blob=img_buffer.getvalue(),
                    meta={
                        "mime_type": "image/png",
                        "file_name": output_filename
                    }
                )
            
            # Send completion message
            yield self.create_text_message(f"Successfully converted {total_pages} pages to PNG images.")
            
            doc.close()
            
        except ValueError as e:
            raise
        except Exception as e:
            raise Exception(f"Error converting PDF to PNG: {str(e)}")
    
    def get_runtime_parameters(
        self,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> list[ToolParameter]:
        """
        Get the runtime parameters for the PDF to PNG conversion tool.
        
        Returns:
            list[ToolParameter]: List of tool parameters
        """
        parameters = [
            ToolParameter(
                name="pdf_content",
                label=I18nObject(en_US="PDF Content", zh_Hans="PDF 内容"),
                human_description=I18nObject(
                    en_US="PDF file to convert to PNG images",
                    zh_Hans="要转换为PNG图片的PDF文件",
                ),
                type=ToolParameter.ToolParameterType.FILE,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
                file_accepts=["application/pdf"],
            ),
            ToolParameter(
                name="zoom",
                label=I18nObject(en_US="Zoom Factor", zh_Hans="缩放因子"),
                human_description=I18nObject(
                    en_US="Zoom factor for image quality (default is 2)",
                    zh_Hans="图像质量的缩放因子（默认为2）",
                ),
                type=ToolParameter.ToolParameterType.NUMBER,
                form=ToolParameter.ToolParameterForm.FORM,
                required=False,
                default=2,
            ),
        ]
        return parameters
