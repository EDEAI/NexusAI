from urllib.parse import urlencode, urljoin
from collections.abc import Generator
from typing import Any
import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class RookieRssTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        try:
            # 1. 参数校验与类型转换
            base_url: str = self.runtime.credentials["daily_hot_url"]
            platform: str = self._get_required_param(tool_parameters, "platform", str)
            result_type: str = tool_parameters.get("result_type", "json")
            result_type: str = "json"
            result_num: int = int(tool_parameters.get("result_num", 10))  # 默认取10条

            # 2. 安全构建URL
            endpoint = f"/{platform.strip('/')}"
            query_params = {
                "rss": "true" if result_type.lower() == "rss" else None,
                "limit": result_num
            }
            
            # 过滤None值参数
            query_params = {k: v for k, v in query_params.items() if v is not None}
            
            # 使用标准库构建URL
            full_url = urljoin(base_url, endpoint)
            if query_params:
                full_url += "?" + urlencode(query_params, doseq=True)

            print(f"Invoke RookieRssTool with {full_url}")
            # 3. 带异常处理的HTTP请求
            response = requests.get(
                full_url,
                headers={"User-Agent": "Dify-RookieRssTool/1.0"},
                timeout=10
            )
            response.raise_for_status()

            # 4. 响应数据解析
            data = response.json()
            print(data)
            
            # 5. 返回标准化数据结构
            yield self.create_json_message({
                "status": "success",
                "code": data.get('code', 200),
                "articles": self._format_articles(data),
                "pagination": {
                    "total": data.get('total', 0),
                    "returned": len(data.get('data', []))
                }
            })

        except KeyError as e:
            self._log_error(f"Missing required credential: {e}")
        except ValueError as e:
            self._log_error(f"Invalid parameter value: {e}")
        except requests.RequestException as e:
            self._log_error(f"API request failed: {str(e)}")
        except Exception as e:
            self._log_error(f"Unexpected error: {str(e)}")

    def _get_required_param(self, params: dict, key: str, expected_type: type) -> Any:
        """安全获取并校验必须参数"""
        value = params.get(key)
        if value is None:
            raise KeyError(f"Missing required parameter: {key}")
        if not isinstance(value, expected_type):
            raise ValueError(f"Invalid type for {key}, expected {expected_type.__name__}")
        return value

    def _log_error(self, message):
        """错误日志记录（可根据需要对接日志系统）"""
        print(f"[RookieRss] ERROR: {message}")
    def _format_articles(self, raw_data: dict) -> list[dict]:
        """将原始数据转换为前端友好的结构"""
        formatted = []
        for idx, item in enumerate(raw_data.get('data', []), 1):
            formatted.append({
                # 基础字段
                "rank": idx,
                "id": item.get('id'),
                "title": item.get('title'),
                "author": item.get('author'),
                "hot_score": item.get('hot'),
                
                # 链接优化
                "links": {
                    "pc": item.get('url'),
                    "mobile": item.get('mobileUrl'),
                },
                
                # 语义化元数据
                "metadata": {
                    "platform": raw_data.get('name'),
                    "list_type": raw_data.get('type'),
                    "update_time": raw_data.get('updateTime')
                }
            })
        return formatted