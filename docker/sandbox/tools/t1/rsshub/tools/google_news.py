import json
import logging
import urllib.parse
from typing import Dict, Any, List, Generator

import requests
from pydantic import BaseModel, Field

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)


class GoogleNewsRequest(BaseModel):
    base_url: str = Field(default="https://rsshub.app", description="RSSHub base URL")
    access_key: str = Field(default="", description="Access key for RSSHub routes")
    category: str = Field(..., description="Category title of Google News")
    language_code: str = Field(..., description="Language code for Google News content")
    country_code: str = Field(..., description="Country or region code for Google News content")
    country_edition: str = Field(..., description="Country edition for Google News")
    limit: int = Field(default=10, description="Maximum number of items to return")


class GoogleNewsTool(Tool):
    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Process the request and return the response."""
        try:
            req = GoogleNewsRequest(**tool_parameters)
            
            # Encode category for URL
            encoded_category = urllib.parse.quote(req.category)
            
            # Construct the locale parameter
            locale = f"hl={req.language_code}&gl={req.country_code}&ceid={req.country_edition}"
            
            # Construct the RSSHub URL for Google News
            route = f"/google/news/{encoded_category}/{locale}"
            
            # 确保route以/开头
            if not route.startswith("/"):
                route = "/" + route
                
            # 确保base_url以/结尾
            base_url = req.base_url
            if not base_url.endswith("/"):
                base_url = base_url + "/"
                
            # 构建完整URL
            url = base_url.rstrip("/") + route
            
            # 如果提供了访问密钥，添加到URL中
            if req.access_key:
                # 检查URL是否已经有查询参数
                if "?" in url:
                    url += f"&key={req.access_key}"
                else:
                    url += f"?key={req.access_key}"
            
            logger.info(f"Fetching Google News from: {url}")
            
            # 获取RSS源
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            # 获取命名空间
            namespaces = {'': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            
            # 提取标题和描述
            channel = root.find('.//channel', namespaces)
            if channel is None:
                channel = root
                
            title = channel.findtext('./title', '未知标题', namespaces)
            description = channel.findtext('./description', '无描述', namespaces)
            
            # 提取条目
            items = channel.findall('./item', namespaces)
            
            # 限制条目数量
            if len(items) > req.limit:
                items = items[:req.limit]
            
            # 构建结果
            result = {
                "title": title,
                "description": description,
                "url": url,
                "items": []
            }
            
            for item in items:
                item_title = item.findtext('./title', '', namespaces)
                item_link = item.findtext('./link', '', namespaces)
                item_description = item.findtext('./description', '', namespaces)
                item_pubDate = item.findtext('./pubDate', '', namespaces)
                
                result["items"].append({
                    "title": item_title,
                    "link": item_link,
                    "description": item_description,
                    "pubDate": item_pubDate
                })
            
            # 使用Tool类中的辅助方法创建JSON消息
            yield self.create_json_message(result)
            
        except Exception as e:
            logger.error(f"Error fetching Google News: {str(e)}")
            error_message = f"Error fetching Google News: {str(e)}"
            # 使用Tool类中的辅助方法创建文本消息
            yield self.create_text_message(error_message)


if __name__ == "__main__":
    # 注意：这里只是为了测试，实际运行时Tool类会由Dify框架初始化
    print("This is a test module. Run the main.py file to start the plugin.") 