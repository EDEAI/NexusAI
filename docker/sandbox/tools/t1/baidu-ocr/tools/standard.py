from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from aip import AipOcr
import requests
from io import BytesIO

class StandardOCRTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取凭证
        credentials = self.runtime.credentials
        client = AipOcr(
            credentials['app_id'],
            credentials['api_key'],
            credentials['secret_key']
        )
        # def get_file_content(filePath):
        #     print(f"filePath::::{filePath.url}")
        #     with open(filePath.url, "rb") as fp:
        #         return fp.read()
            
        def get_file_content(file_url):
            response = requests.get(file_url)
            response.raise_for_status()  # 如果请求失败，抛出异常
            return response.content
                
        # 获取文件
        image_file = tool_parameters['file_location']
        print("image_file:::",image_file)
        if not image_file:
            raise ValueError("File is required")
        
        # 读取文件内容
        image_data = get_file_content(image_file.url)
        
        file_type = tool_parameters['type']

        # 设置选项
        options = {}
        if 'language_type' in tool_parameters:
            options['language_type'] = tool_parameters['language_type']
        if file_type == 'pdf' and 'pdf_file_num' in tool_parameters:
            options['pdf_file_num'] = tool_parameters['pdf_file_num']
        # 调用标准OCR接口
        response = client.basicGeneral(image_data, options)
        
        # 处理结果
        if 'words_result' in response:
            texts = [res['words'] for res in response['words_result']]
            result = {
                "text": "\n".join(texts),
                "full_result": response
            }
            yield self.create_text_message(result["text"])
            yield self.create_json_message(result)
        else:
            yield self.create_text_message(f"OCR failed: {response.get('error_msg', 'Unknown error')}")