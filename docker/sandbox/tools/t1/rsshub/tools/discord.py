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

class DiscordTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        route_type = tool_parameters.get("route_type", "channel")
        channel_id = tool_parameters.get("channel_id", "")
        guild_id = tool_parameters.get("guild_id", "")
        search_params = tool_parameters.get("search_params", "")
        discord_authorization = tool_parameters.get("discord_authorization", "")
        limit = int(tool_parameters.get("limit", 10))
        base_url = tool_parameters.get("base_url", "https://rsshub.app")
        access_key = tool_parameters.get("access_key", "")
        
        # 确保base_url以/结尾
        if not base_url.endswith("/"):
            base_url = base_url + "/"
            
        # 根据路由类型构建不同的路由
        route = ""
        
        if route_type == "channel":
            if not channel_id:
                yield self.create_text_message("频道路由需要提供频道ID")
                return
                
            if not discord_authorization:
                yield self.create_text_message("需要提供Discord授权令牌")
                return
                
            route = f"/discord/channel/{channel_id}"
            
        elif route_type == "search":
            if not guild_id:
                yield self.create_text_message("搜索路由需要提供服务器ID")
                return
                
            if not discord_authorization:
                yield self.create_text_message("需要提供Discord授权令牌")
                return
                
            route = f"/discord/search/{guild_id}"
            
            # 添加搜索参数（如果有）
            if search_params:
                route = f"{route}/{search_params}"
                
        else:
            yield self.create_text_message(f"不支持的路由类型: {route_type}")
            return
            
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
            # 设置请求头
            headers = {
                "Authorization": discord_authorization
            }
            
            # 获取RSS源
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 解析XML
            root = ET.fromstring(response.content)
            
            # 获取命名空间
            namespaces = {'': root.tag.split('}')[0].strip('{')} if '}' in root.tag else {}
            
            # 提取标题和描述
            channel = root.find('.//channel', namespaces)
            if channel is None:
                channel = root
                
            # 根据路由类型设置默认标题
            default_title = ""
            if route_type == "channel":
                default_title = f"Discord 频道 {channel_id}"
            elif route_type == "search":
                default_title = f"Discord 服务器 {guild_id} 搜索结果"
                if search_params:
                    default_title += f": {search_params}"
                
            title = channel.findtext('./title', default_title, namespaces)
            description = channel.findtext('./description', f"Discord RSS 源", namespaces)
            
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
                "route_type": route_type,
                "route_info": {
                    "channel_id": channel_id if route_type == "channel" else None,
                    "guild_id": guild_id if route_type == "search" else None,
                    "search_params": search_params if route_type == "search" and search_params else None
                }
            }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            error_message = f"获取Discord RSS源失败: {str(e)}"
            yield self.create_text_message(error_message) 