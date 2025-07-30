from collections.abc import Generator
from typing import Any
import requests
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, urlparse, parse_qs, urlencode

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RsshubTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        route = tool_parameters.get("route", "")
        limit = int(tool_parameters.get("limit", 10))
        base_url = tool_parameters.get("base_url", "https://rsshub.app")
        access_key = tool_parameters.get("access_key", "")
        
        # 确保route以/开头
        if not route.startswith("/"):
            route = "/" + route
            
        # 确保base_url以/结尾
        if not base_url.endswith("/"):
            base_url = base_url + "/"
            
        # 构建完整URL
        url = urljoin(base_url, route)
        
        # 如果提供了访问密钥，添加到URL中
        if access_key:
            # 解析URL
            parsed_url = urlparse(url)
            # 获取现有查询参数
            query_params = parse_qs(parsed_url.query)
            # 添加key参数
            query_params['key'] = [access_key]
            # 重新构建查询字符串
            new_query = urlencode(query_params, doseq=True)
            # 替换URL中的查询部分
            url_parts = list(parsed_url)
            url_parts[4] = new_query
            # 重新组合URL
            url = urljoin(base_url, route + "?" + new_query)
        
        try:
            # 获取RSS源
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析XML
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
            entries = []
            items = channel.findall('./item', namespaces)
            
            for item in items[:limit]:
                item_title = item.findtext('./title', '无标题', namespaces)
                item_link = item.findtext('./link', '', namespaces)
                item_pubDate = item.findtext('./pubDate', '', namespaces)
                item_description = item.findtext('./description', '', namespaces)
                
                # 清理HTML标签
                clean_content = re.sub(r'<.*?>', '', item_description)
                clean_content = html.unescape(clean_content)
                
                # 格式化日期
                published = item_pubDate
                try:
                    if published:
                        dt = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                        published = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    # 如果日期解析失败，保持原样
                    pass
                
                entries.append({
                    'title': item_title,
                    'link': item_link,
                    'published': published,
                    'content': clean_content[:500] + ('...' if len(clean_content) > 500 else '')
                })
            
            # 返回结果
            result = {
                "title": title,
                "description": description,
                "url": url,
                "entries": entries
            }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            yield self.create_text_message(f"获取RSS源失败: {str(e)}")
