from collections.abc import Generator
from typing import Any
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from ragflow_api import RagflowClient
import re


class RagflowApiTool(Tool):
    """
    創建數據集工具
    """
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        調用創建數據集API
        
        Args:
            tool_parameters: 包含創建數據集所需的參數
                - name: 數據集名稱（必填）
                - description: 數據集描述                
        Returns:
            創建結果信息
        """
        try:
            # 獲取憑證信息
            app_id = str(self.runtime.credentials.get("app_key"))
            app_url = str(self.runtime.credentials.get("app_url"))

            # 創建客戶端
            client = RagflowClient(app_id, app_url)
            
            # 獲取必要參數
            name = tool_parameters.get("name", '')
            if not name:
                yield self.create_text_message('Dataset name is required')
                return
                
            # 構建請求數據
            parsed_data = {
                "name": name
            }
            
            # 添加可選參數
            optional_fields = ["description"]
            
            for field in optional_fields:
                value = tool_parameters.get(field, None)
                if value is not None:
                    parsed_data[field] = value
            
            # 發送請求創建數據集
            res = client.post(route_method='/api/v1/datasets', data_obj=parsed_data)
            
            # 處理響應
            try:
                data = res.json().get("data", {})
                if not data:
                    yield self.create_text_message("Create dataset failed")
                    return
                    
                yield self.create_json_message({
                    "result": data
                })
            except Exception as e:
                yield self.create_text_message(f"Error occurred while processing the response: {str(e)}")
                return
                
        except Exception as e:
            yield self.create_text_message(f"Error occurred while creating the dataset: {str(e)}")
            return