from collections.abc import Generator
from typing import Any
import requests
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, quote, urlencode, parse_qs, urlparse

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ThreadsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        route_type = tool_parameters.get("route_type", "user")
        username = tool_parameters.get("username", "")
        base_url = tool_parameters.get("base_url", "https://rsshub.app")
        access_key = tool_parameters.get("access_key", "")
        show_author_in_title = tool_parameters.get("show_author_in_title", True)
        show_author_in_desc = tool_parameters.get("show_author_in_desc", True)
        show_quoted_in_title = tool_parameters.get("show_quoted_in_title", True)
        show_emoji_for_quotes_and_reply = tool_parameters.get("show_emoji_for_quotes_and_reply", True)
        replies = tool_parameters.get("replies", True)
        show_author_avatar_in_desc = tool_parameters.get("show_author_avatar_in_desc", False)
        show_quoted_author_avatar_in_desc = tool_parameters.get("show_quoted_author_avatar_in_desc", False)
        limit = int(tool_parameters.get("limit", 10))
        
        # 验证必要参数
        if not username:
            yield self.create_text_message("Threads用户名不能为空")
            return
            
        # 确保base_url以/结尾
        if not base_url.endswith("/"):
            base_url = base_url + "/"
            
        # 构建路由和查询参数
        route = ""
        query_params = {}
        
        if route_type == "user":
            route = f"/threads/{username}"
            
            # 添加显示选项
            query_params["showAuthorInTitle"] = "true" if show_author_in_title else "false"
            query_params["showAuthorInDesc"] = "true" if show_author_in_desc else "false"
            query_params["showQuotedInTitle"] = "true" if show_quoted_in_title else "false"
            query_params["showEmojiForQuotesAndReply"] = "true" if show_emoji_for_quotes_and_reply else "false"
            query_params["replies"] = "true" if replies else "false"
            query_params["showAuthorAvatarInDesc"] = "true" if show_author_avatar_in_desc else "false"
            query_params["showQuotedAuthorAvatarInDesc"] = "true" if show_quoted_author_avatar_in_desc else "false"
            
            # 如果提供了访问密钥，添加到查询参数中
            if access_key:
                query_params["key"] = access_key
        else:
            yield self.create_text_message(f"不支持的路由类型: {route_type}")
            return
            
        # 构建最终URL
        url = urljoin(base_url, route)
        if query_params:
            url = f"{url}?{urlencode(query_params)}"
            
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
                
            title = channel.findtext('./title', f'{username} 的 Threads', namespaces)
            description = channel.findtext('./description', f'{username} 的 Threads 订阅源', namespaces)
            
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
                "entries": entries,
                "username": username,
                "display_options": {
                    "show_author_in_title": show_author_in_title,
                    "show_author_in_desc": show_author_in_desc,
                    "show_quoted_in_title": show_quoted_in_title,
                    "show_emoji_for_quotes_and_reply": show_emoji_for_quotes_and_reply,
                    "replies": replies,
                    "show_author_avatar_in_desc": show_author_avatar_in_desc,
                    "show_quoted_author_avatar_in_desc": show_quoted_author_avatar_in_desc
                }
            }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            error_message = f"获取Threads RSS源失败: {str(e)}"
            yield self.create_text_message(error_message) 