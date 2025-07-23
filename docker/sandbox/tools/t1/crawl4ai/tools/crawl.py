import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class Crawl4AICrawlTool(Tool):
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
        
        payload = {
            "urls": [url],
            "crawler_config": {
                "type": "CrawlerRunConfig",
                "params": {
                    "css_selector": css_selector,
                    "excluded_tags": excluded_tags,
                    "stream": False,
                    "cache_mode": "BYPASS"
                }
            }
        }

        try:
            # 发送请求到Crawl4AI服务
            response = requests.post(
                f"{server_url}/crawl",
                json=payload
            )
            
            # 检查响应状态
            response.raise_for_status()

            result = response.json()["results"][0]  # 因为只取一个
            if output_format == "html":
                yield self.create_text_message(result.get("html", ""))
            elif output_format == "cleaned_html":
                yield self.create_text_message(result.get("cleaned_html", ""))
            else:
                markdown_content = result.get("markdown", "")["raw_markdown"]
                yield self.create_text_message(markdown_content)
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
