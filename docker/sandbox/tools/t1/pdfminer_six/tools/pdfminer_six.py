from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from io import StringIO, BytesIO
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
import re

class PdfminerSixTool(Tool):
    # 支持的输出格式及其对应的 MIME 类型
    OUTPUT_TYPES = {
        "text": "text/plain",
        "xml": "application/xml",
        "html": "text/html",
        "tag": "text/plain",
        "markdown": "text/markdown",
    }
    
    # pdfminer.six 原生支持的输出格式
    NATIVE_OUTPUT_TYPES = {"text", "xml", "html", "tag"}

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取文件元数据
        file_blob = tool_parameters.get("files")
        # 获取输出格式，默认为 text
        output_type = tool_parameters.get("output_type", "text")

        # 验证输出格式
        if output_type not in self.OUTPUT_TYPES:
            yield self.create_text_message(
                f"Invalid output type. Supported types: {', '.join(self.OUTPUT_TYPES.keys())}"
            )
            return

        # 检查文件是否为PDF
        if file_blob.extension != ".pdf":
            yield self.create_text_message("The uploaded file is not a PDF.")
            yield self.create_json_message(
                {
                    "status": "error",
                    "message": "The uploaded file is not a PDF.",
                    "results": [],
                }
            )
            return

        try:
            output_string = StringIO()
            pdf_file = BytesIO(file_blob.blob)
            
            # 确定实际处理时使用的输出格式
            processing_output_type = output_type
            if output_type not in self.NATIVE_OUTPUT_TYPES:
                # 如果请求的格式不是原生支持的，先提取为文本
                processing_output_type = "text"

            # 使用指定的输出格式提取文本
            extract_text_to_fp(
                pdf_file,
                output_string,
                laparams=LAParams(),
                output_type=processing_output_type,
                codec=None,
            )

            content = output_string.getvalue()
            
            # 如果请求的是 markdown 格式但实际处理为文本，则转换为 markdown
            if output_type == "markdown" and processing_output_type == "text":
                content = self._convert_text_to_markdown(content)
                
            mime_type = self.OUTPUT_TYPES[output_type]

            # 返回处理结果
            yield self.create_text_message(
                f"PDF processed successfully in {output_type} format\n"
            )
            yield self.create_blob_message(blob=content, meta={"mime_type": mime_type})
            yield self.create_json_message(
                {
                    "status": "success",
                    "output_type": output_type,
                    "mime_type": mime_type,
                }
            )

        except Exception as e:
            yield self.create_text_message(f"Error processing file: {str(e)}")
            yield self.create_json_message(
                {
                    "status": "error",
                    "message": f"Error processing file: {str(e)}",
                    "results": [],
                }
            )
        finally:
            # 清理资源
            pdf_file.close()
            output_string.close()
            
    def _convert_text_to_markdown(self, text: str) -> str:
        """
        将提取的文本转换为Markdown格式
        """
        # 分割为段落
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 处理段落
        markdown_paragraphs = []
        for paragraph in paragraphs:
            # 清理空白行
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # 检测标题行 (假设全大写或以数字开头的行是标题)
            if paragraph.isupper() or re.match(r'^\d+\.?\s+', paragraph):
                level = 3 if paragraph.isupper() else 4
                markdown_paragraphs.append(f"{'#' * level} {paragraph}")
            else:
                markdown_paragraphs.append(paragraph)
        
        return "\n\n".join(markdown_paragraphs)