from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import requests
import os
import base64
from io import BytesIO
from PIL import Image
import imghdr
from urllib.parse import urlparse


import logging
from dify_plugin.config.logger_format import plugin_logger_handler

# 使用自定义处理器设置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class OCRToMarkdownTool(Tool):
    def _convert_rgba_if_needed(self, file_content: BytesIO, filename: str) -> tuple[BytesIO, str]:
        """仅在图片是RGBA模式时转换为RGB JPEG"""
        file_content.seek(0)
        try:
            img = Image.open(file_content)
            if img.mode == 'RGBA':
                img = img.convert('RGB')
                converted = BytesIO()
                img.save(converted, format='JPEG', quality=100)
                converted.seek(0)
                return converted, os.path.splitext(filename)[0] + '.jpg'
            file_content.seek(0)  # 确保指针重置
            return file_content, filename
        except Exception as e:
            raise ValueError(f"RGBA图片转换失败: {str(e)}")

    def _embed_images(self, markdown: str, images: dict) -> str:
        """将OCR返回的图片base64嵌入Markdown"""
        for img_name, img_data in images.items():
            if not img_data.startswith('data:'):
                markdown = markdown.replace(
                    f"![]({img_name})",
                    f"![](data:image/jpeg;base64,{img_data})"
                )
        return markdown

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        
        uploaded_file = tool_parameters.get('file')
        if not uploaded_file:
            yield self.create_text_message("请上传文件")
            return

        service_url = tool_parameters.get('service_url')
        if not service_url:
            yield self.create_text_message("请设置正确OCR请求路径")
            return
        
        logger.info("OCR Service URL: %s", service_url)

        try:
            # 1. 下载文件
            response = requests.get(uploaded_file.url)
            if response.status_code != 200:
                yield self.create_text_message(f"文件下载失败，状态码: {response.status_code}")
                return

            file_content = BytesIO(response.content)
            filename = uploaded_file.filename
            
            # 2. 检查是否为图片
            file_type = imghdr.what(file_content)
            if file_type:  # 如果是图片文件
                try:
                    file_content, filename = self._convert_rgba_if_needed(file_content, filename)
                except ValueError as e:
                    yield self.create_text_message(str(e))
                    return

            # 3. 发送到OCR服务
            files = {'file': (filename, file_content)}
            ocr_response = requests.post(
                service_url,
                files=files,
                data={
                    'force_ocr': 'true' if file_type else 'false',
                    'paginate_output': 'false',
                    'output_format': 'markdown'
                }
            )

            if ocr_response.status_code != 200:
                yield self.create_text_message(f"OCR处理失败，状态码: {ocr_response.status_code}")
                return

            result = ocr_response.json()
            if not result.get('success', False):
                yield self.create_text_message(f"OCR处理失败: {result.get('error', '未知错误')}")
                return

            # 4. 处理返回的图片引用
            markdown_content = result.get('output', '')
            if 'images' in result and markdown_content:
                markdown_content = self._embed_images(markdown_content, result['images'])

            # 5. 返回最终Markdown
            yield self.create_blob_message(
                markdown_content.encode('utf-8'),
                meta={
                    "mime_type": "text/markdown",
                    "filename": os.path.splitext(filename)[0] + ".md"
                }
            )

        except requests.exceptions.RequestException as e:
            yield self.create_text_message(f"网络请求失败: {str(e)}")
        except Exception as e:
            yield self.create_text_message(f"处理失败: {str(e)}")