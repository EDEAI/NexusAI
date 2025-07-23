import io
from collections.abc import Generator
from typing import Any, Optional, List

import PyPDF2
from dify_plugin.entities import I18nObject
from dify_plugin.entities.tool import ToolInvokeMessage, ToolParameter
from dify_plugin import Tool
from dify_plugin.file.file import File

class PDFMultiPagesExtractorTool(Tool):
    """
    A tool for extracting multiple pages from PDF files using flexible page specifications.
    This tool takes a PDF file (File object) and page specifications as strings.
    One string ('fixed_pages') is optional and specifies fixed pages to always include (e.g., "1-3,5").
    The other string ('dynamic_pages') specifies the dynamic pages to extract (e.g., "4,6-8").
    The resulting PDF will contain the specified fixed pages followed by the specified dynamic pages, preserving the order and allowing duplicates as defined in the input strings.

    Parameters:
        pdf_content (File): Dify File object representing the PDF.
        fixed_pages (str, optional): String specifying fixed page numbers/ranges (1-indexed). Order and duplicates are preserved. Examples: "1-3", "5", "1,3,1-2". Default: "".
        dynamic_pages (str): String specifying dynamic page numbers/ranges to extract (1-indexed). Order and duplicates are preserved. Examples: "1-3", "5", "1,3,1-2". Required. Default: "1".
    """

    @staticmethod
    def _parse_page_string(page_str: str, total_pages: int) -> List[int]:
        """
        Parses a page string (e.g., "1-3,5,1-2") into a list of 0-based page indices,
        preserving order and duplicates. Validates against total_pages.
        """
        if not page_str:
            return []

        indices: List[int] = []
        parts = page_str.replace(" ", "").split(',')

        for part in parts:
            if not part:
                continue
            if '-' in part:
                range_parts = part.split('-', 1)
                if len(range_parts) != 2:
                    raise ValueError(f"Invalid range format: '{part}'. Use 'start-end'.")

                start_str, end_str = range_parts

                try:
                    start = int(start_str) if start_str else 1
                    end = int(end_str) if end_str else total_pages
                except ValueError:
                    raise ValueError(f"Invalid page number in range: '{part}'. Pages must be integers.")

                if start < 1 or end < 1:
                    raise ValueError(f"Page numbers must be positive: '{part}'.")
                if start > end:
                    raise ValueError(f"Start page cannot be greater than end page in range: '{part}'.")
                if start > total_pages or end > total_pages:
                    raise ValueError(f"Page number out of range in '{part}'. PDF has {total_pages} pages (1 to {total_pages}).")

                indices.extend(range(start - 1, end))
            else:
                try:
                    page_num = int(part)
                except ValueError:
                    raise ValueError(f"Invalid page number: '{part}'. Pages must be integers.")

                if page_num < 1:
                     raise ValueError(f"Page number must be positive: '{part}'.")
                if page_num > total_pages:
                    raise ValueError(f"Page number {page_num} out of range. PDF has {total_pages} pages (1 to {total_pages}).")

                indices.append(page_num - 1)

        if not indices:
             raise ValueError(f"No valid page numbers found in specification: '{page_str}'.")

        return indices

    def _invoke(
        self,
        tool_parameters: dict[str, Any],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # Get and validate PDF content
            pdf_content = tool_parameters.get("pdf_content")
            if not isinstance(pdf_content, File):
                raise ValueError("PDF content must be a File object")

            # Fetch page specification strings
            dynamic_pages_str = tool_parameters.get("dynamic_pages")
            if not dynamic_pages_str or not isinstance(dynamic_pages_str, str):
                 raise ValueError("Missing or invalid required parameter: dynamic_pages (must be a non-empty string)")
            fixed_pages_str = tool_parameters.get("fixed_pages", "") # Optional, defaults to empty string
            if not isinstance(fixed_pages_str, str):
                 raise ValueError("Invalid optional parameter: fixed_pages (must be a string)")


            # Get the PDF content directly from the File object
            pdf_bytes = pdf_content.blob
            original_filename = pdf_content.filename or "document"
            pdf_file = io.BytesIO(pdf_bytes)

            try:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
            except Exception as e:
                raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

            total_pages = len(pdf_reader.pages)
            if total_pages == 0:
                raise ValueError("The provided PDF file has no pages.")

            # Parse page strings into 0-based indices
            try:
                 fixed_page_indices = self._parse_page_string(fixed_pages_str, total_pages)
                 dynamic_page_indices = self._parse_page_string(dynamic_pages_str, total_pages)
            except ValueError as e:
                 # Re-raise parsing errors with context
                 raise ValueError(f"Invalid page specification: {e}")

            use_fixed = bool(fixed_page_indices)

            # Create the output PDF
            output = PyPDF2.PdfWriter()

            # Add fixed pages first, preserving order and duplicates
            if use_fixed:
                for index in fixed_page_indices:
                    output.add_page(pdf_reader.pages[index])

            # Add dynamic pages, preserving order and duplicates
            for index in dynamic_page_indices:
                 output.add_page(pdf_reader.pages[index])

            if len(output.pages) == 0:
                 raise ValueError("The specified page numbers resulted in an empty PDF.")

            page_buffer = io.BytesIO()
            output.write(page_buffer)
            page_buffer.seek(0)

            # Generate descriptive filename
            if original_filename.lower().endswith('.pdf'):
                base_filename = original_filename[:-4]
            else:
                base_filename = original_filename

            dynamic_desc = dynamic_pages_str.replace(',', '_').replace('-', 'to')
            if use_fixed:
                fixed_desc = fixed_pages_str.replace(',', '_').replace('-', 'to')
                output_filename = f"{base_filename}_fixed_{fixed_desc}_plus_{dynamic_desc}.pdf"
                success_message = f"Successfully extracted fixed pages '{fixed_pages_str}' followed by dynamic pages '{dynamic_pages_str}'"
            else:
                output_filename = f"{base_filename}_pages_{dynamic_desc}.pdf"
                success_message = f"Successfully extracted pages '{dynamic_pages_str}' from PDF"

            yield self.create_text_message(success_message)

            yield self.create_blob_message(
                blob=page_buffer.getvalue(),
                meta={
                    "mime_type": "application/pdf",
                    "file_name": output_filename
                },
            )

        except ValueError as e:
            # Catch specific ValueErrors (parsing, validation) and raise them
            raise e
        except Exception as e:
            # Catch general exceptions
            raise Exception(f"An unexpected error occurred during PDF processing: {str(e)}")

    def get_runtime_parameters(
        self,
        conversation_id: Optional[str] = None,
        app_id: Optional[str] = None,
        message_id: Optional[str] = None,
    ) -> list[ToolParameter]:
        """
        Get the runtime parameters for the PDF multi-pages extractor tool.

        Returns:
            list[ToolParameter]: List of tool parameters.
        """
        parameters = [
            ToolParameter(
                name="pdf_content",
                label=I18nObject(en_US="PDF Content", zh_Hans="PDF 内容"),
                human_description=I18nObject(
                    en_US="The PDF file to process.",
                    zh_Hans="要处理的 PDF 文件。",
                ),
                type=ToolParameter.ToolParameterType.FILE,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
                file_accepts=["application/pdf"],
            ),
            ToolParameter(
                name="fixed_pages",
                label=I18nObject(en_US="Fixed Pages (Optional)", zh_Hans="固定页码（可选）"),
                human_description=I18nObject(
                    en_US='Pages to always include at the beginning. Order and duplicates are preserved. Examples: "1-3", "5", "1,3,1-2". Leave empty if none.',
                    zh_Hans='始终包含在开头的页面。保留顺序和重复项。例如："1-3", "5", "1,3,1-2"。如果没有则留空。',
                ),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=False,
                default="",
            ),
            ToolParameter(
                name="dynamic_pages",
                label=I18nObject(en_US="Dynamic Pages", zh_Hans="动态页码"),
                human_description=I18nObject(
                    en_US='Pages to extract. Order and duplicates are preserved. Examples: "1-3", "5", "1,3,1-2".',
                    zh_Hans='要提取的页面。保留顺序和重复项。例如："1-3", "5", "1,3,1-2"。',
                ),
                type=ToolParameter.ToolParameterType.STRING,
                form=ToolParameter.ToolParameterForm.FORM,
                required=True,
                default="1",
            ),
        ]
        return parameters
