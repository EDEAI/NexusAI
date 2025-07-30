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

class TwitterTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        route_type = tool_parameters.get("route_type", "user")
        username = tool_parameters.get("username", "")
        keyword = tool_parameters.get("keyword", "")
        list_id = tool_parameters.get("list_id", "")
        limit = int(tool_parameters.get("limit", 10))
        base_url = tool_parameters.get("base_url", "https://rsshub.app")
        access_key = tool_parameters.get("access_key", "")
        exclude_replies = tool_parameters.get("exclude_replies", False)
        exclude_rts = tool_parameters.get("exclude_rts", False)
        
        # 确保base_url以/结尾
        if not base_url.endswith("/"):
            base_url = base_url + "/"
            
        # 根据路由类型构建不同的路由
        route = ""
        
        if route_type == "user":
            if not username:
                yield self.create_text_message("用户路由需要提供用户名")
                return
                
            # 移除用户名中的@符号（如果有）
            username = username.lstrip('@')
            route = f"/twitter/user/{username}"
            
            # 添加额外参数
            route_params = []
            if exclude_replies:
                route_params.append("exclude_replies")
            if exclude_rts:
                route_params.append("exclude_rts")
                
            # 如果有额外参数，添加到路由中
            if route_params:
                route = f"{route}/{','.join(route_params)}"
                
        elif route_type == "keyword":
            if not keyword:
                yield self.create_text_message("关键词路由需要提供关键词")
                return
                
            route = f"/twitter/keyword/{keyword}"
            
        elif route_type == "list":
            if not list_id:
                yield self.create_text_message("列表路由需要提供列表ID")
                return
                
            route = f"/twitter/list/{list_id}"
            
        elif route_type == "home":
            route = "/twitter/home"
            
        elif route_type == "home_latest":
            route = "/twitter/home_latest"
            
        elif route_type == "likes":
            if not username:
                yield self.create_text_message("喜欢路由需要提供用户名")
                return
                
            # 移除用户名中的@符号（如果有）
            username = username.lstrip('@')
            route = f"/twitter/likes/{username}"
            
        elif route_type == "media":
            if not username:
                yield self.create_text_message("媒体路由需要提供用户名")
                return
                
            # 移除用户名中的@符号（如果有）
            username = username.lstrip('@')
            route = f"/twitter/media/{username}"
            
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
                
            # 根据路由类型设置默认标题
            default_title = ""
            if route_type == "user":
                default_title = f"@{username} 的推文"
            elif route_type == "keyword":
                default_title = f"关于 {keyword} 的推文"
            elif route_type == "list":
                default_title = f"Twitter 列表 {list_id}"
            elif route_type == "home":
                default_title = "Twitter 主页时间线"
            elif route_type == "home_latest":
                default_title = "Twitter 最新主页时间线"
            elif route_type == "likes":
                default_title = f"@{username} 喜欢的推文"
            elif route_type == "media":
                default_title = f"@{username} 的媒体推文"
                
            title = channel.findtext('./title', default_title, namespaces)
            description = channel.findtext('./description', f"Twitter RSS 源", namespaces)
            
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
                "filters": {
                    "exclude_replies": exclude_replies if route_type == "user" else None,
                    "exclude_rts": exclude_rts if route_type == "user" else None
                }
            }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            error_message = f"获取Twitter RSS源失败: {str(e)}"
            yield self.create_text_message(error_message) 