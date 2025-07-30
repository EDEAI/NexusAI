import requests
from collections.abc import Generator
from typing import Any, Dict, List

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import logging


class Crawl4AICrawlDirectTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """使用Crawl4AI服务提取网页内容"""
        # 获取参数
        url = tool_parameters.get("url")
        css_selector = tool_parameters.get("css_selector")
        excluded_tags_str = tool_parameters.get("excluded_tags", "script,style,noscript")
        output_format = tool_parameters.get("output_format", "markdown")
        
        # 处理排除的标签
        excluded_tags = [tag.strip() for tag in excluded_tags_str.split(",") if tag.strip()]
        
        # 准备请求数据
        server_url = self.runtime.credentials.get("server_url", "").rstrip("/")
        api_token = self.runtime.credentials.get("api_token")
        
        headers = {"Authorization": f"Bearer {api_token}"}
        
        payload = {
            "urls": url,
            "excluded_tags": excluded_tags,
            "output_format": output_format
        }
        
        # 添加可选参数
        if css_selector:
            payload["css_selector"] = css_selector

        logging.info(f"payload: {payload}")
        
        try:
            # 发送请求到Crawl4AI服务
            response = requests.post(
                f"{server_url}/crawl_direct",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 检查响应状态
            response.raise_for_status()

            result = response.json()["result"]
            if output_format == "html":
                yield self.create_text_message(result.get("html", ""))
            else:
                yield self.create_text_message(result.get("markdown", ""))
            
        except requests.exceptions.RequestException as e:
            error_message = f"调用Crawl4AI服务失败: {str(e)}"
            yield self.create_text_message(error_message)
            yield self.create_variable_message("metadata", {
                "url": url,
                "success": False,
                "error": error_message
            })
        except Exception as e:
            error_message = f"处理Crawl4AI响应时出错: {str(e)}"
            yield self.create_text_message(error_message)
            yield self.create_variable_message("metadata", {
                "url": url,
                "success": False,
                "error": error_message
            }) 