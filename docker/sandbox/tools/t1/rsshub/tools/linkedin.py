from collections.abc import Generator
from typing import Any
import requests
import html
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin, quote, urlparse, parse_qs, urlencode

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class LinkedInTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        route_type = tool_parameters.get("route_type", "jobs")
        keywords = tool_parameters.get("keywords", "")
        job_types = tool_parameters.get("job_types", "all")
        exp_levels = tool_parameters.get("exp_levels", "all")
        work_type = tool_parameters.get("work_type", "0")
        time_posted = tool_parameters.get("time_posted", "0")
        geo_id = tool_parameters.get("geo_id", "")
        limit = int(tool_parameters.get("limit", 10))
        base_url = tool_parameters.get("base_url", "https://rsshub.app")
        access_key = tool_parameters.get("access_key", "")
        
        # 确保base_url以/结尾
        if not base_url.endswith("/"):
            base_url = base_url + "/"
            
        # 根据路由类型构建不同的路由
        route = ""
        
        if route_type == "jobs":
            # 构建jobs路由
            route = f"/linkedin/jobs/{job_types}/{exp_levels}"
            
            # 添加关键词（如果有）
            if keywords:
                encoded_keywords = quote(keywords)
                route = f"{route}/{encoded_keywords}"
            
            # 添加额外参数
            params = []
            
            # 添加工作方式
            if work_type != "0":
                params.append(f"f_WT={work_type}")
                
            # 添加发布时间范围
            if time_posted != "0":
                params.append(f"f_TPR={time_posted}")
                
            # 添加地理位置ID
            if geo_id:
                params.append(f"geoId={geo_id}")
                
            # 添加访问密钥
            if access_key:
                params.append(f"key={access_key}")
                
            # 将参数添加到路由中
            if params:
                route = f"{route}/?{'&'.join(params)}"
                
        else:
            yield self.create_text_message(f"不支持的路由类型: {route_type}")
            return
            
        # 构建完整URL
        url = urljoin(base_url, route)
        
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
            if route_type == "jobs":
                default_title = f"LinkedIn 职位搜索"
                if keywords:
                    default_title += f": {keywords}"
                
            title = channel.findtext('./title', default_title, namespaces)
            description = channel.findtext('./description', f"LinkedIn RSS 源", namespaces)
            
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
                    "job_types": job_types,
                    "exp_levels": exp_levels,
                    "work_type": work_type if work_type != "0" else None,
                    "time_posted": time_posted if time_posted != "0" else None,
                    "geo_id": geo_id if geo_id else None
                }
            }
            
            yield self.create_json_message(result)
            
        except Exception as e:
            error_message = f"获取LinkedIn RSS源失败: {str(e)}"
            yield self.create_text_message(error_message)
