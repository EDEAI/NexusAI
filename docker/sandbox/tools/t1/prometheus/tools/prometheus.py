from collections.abc import Generator
from typing import Any, Optional, Dict
import datetime
import requests
from dateutil import parser
from dateutil.relativedelta import relativedelta
import pandas as pd

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from dify_plugin.errors.model import (
    InvokeServerUnavailableError,
)

import traceback

class PrometheusTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取必要参数
        query = tool_parameters.get("query")
        if not query:
            yield self.create_text_message("必须提供PromQL查询语句")
            return

        # 获取可选参数
        start_time = tool_parameters.get("start_time", "1h")  # 默认查询过去1小时
        end_time = tool_parameters.get("end_time", "now")  # 默认当前时间
        step = tool_parameters.get("step", "15s")  # 默认步长15秒
        
        # 获取Prometheus服务器连接信息
        api_url = tool_parameters.get("api_url")
        username = tool_parameters.get("username")
        password = tool_parameters.get("password")
        token = tool_parameters.get("token")

        if not api_url:
            api_url = self.runtime.credentials.get("api_url", '')
            username = self.runtime.credentials.get('username', '')
            password = self.runtime.credentials.get('password', '')
            token = self.runtime.credentials.get('token', '')

        if not api_url:
            raise InvokeServerUnavailableError("required api_url")

        
        # 构建认证头
        headers = {}
        
        if username and password:
            import base64
            auth_str = f"{username}:{password}"
            auth_bytes = auth_str.encode('ascii')
            base64_bytes = base64.b64encode(auth_bytes)
            base64_auth = base64_bytes.decode('ascii')
            headers["Authorization"] = f"Basic {base64_auth}"
        elif token:
            headers["Authorization"] = f"Bearer {token}"
        
        # 处理时间参数
        start_timestamp = self._parse_time(start_time)
        end_timestamp = self._parse_time(end_time)
        
        try:
            # 构建查询URL
            query_url = f"{api_url}/api/v1/query_range"
            params = {
                "query": query,
                "start": start_timestamp,
                "end": end_timestamp,
                "step": step
            }
            
            # 发送请求
            response = requests.get(
                query_url,
                params=params,
                headers=headers,
                timeout=30
            )
            
            # 检查响应
            if response.status_code != 200:
                error_message = f"query failed: HTTP {response.status_code}, {response.text}"
                yield self.create_text_message(error_message)
                return
            
            # 解析响应
            result = response.json()
            
            # 格式化输出
            formatted_result = self._format_result(result)
            
            # 创建Markdown表格
            markdown_table = self._create_markdown_table(formatted_result)
            
            # 返回结果
            yield self.create_text_message(markdown_table)
            yield self.create_json_message(formatted_result)
            
        except Exception as e:
            print(traceback.print_exc())
            raise InvokeServerUnavailableError(f"query error: {str(e)}") from e
    
    def _parse_time(self, time_str: str) -> str:
        """
        解析时间字符串，支持以下格式:
        - 'now': 当前时间
        - 相对时间格式: '1h', '2d', '3w', '4m', '5y' 等
        - RFC3339/ISO8601格式: '2023-01-01T00:00:00Z'
        
        返回Unix时间戳
        """
        now = datetime.datetime.now()
        
        if time_str == "now":
            return str(int(now.timestamp()))
        
        # 尝试解析为相对时间
        if time_str.endswith(('s', 'm', 'h', 'd', 'w', 'M', 'y')):
            unit = time_str[-1]
            try:
                value = int(time_str[:-1])
                
                if unit == 's':  # 秒
                    delta = datetime.timedelta(seconds=value)
                elif unit == 'm':  # 分钟
                    delta = datetime.timedelta(minutes=value)
                elif unit == 'h':  # 小时
                    delta = datetime.timedelta(hours=value)
                elif unit == 'd':  # 天
                    delta = datetime.timedelta(days=value)
                elif unit == 'w':  # 周
                    delta = datetime.timedelta(weeks=value)
                elif unit == 'M':  # 月
                    delta = relativedelta(months=value)
                elif unit == 'y':  # 年
                    delta = relativedelta(years=value)
                
                target_time = now - delta
                return str(int(target_time.timestamp()))
            except (ValueError, TypeError):
                pass
        
        # 尝试解析为绝对时间
        try:
            dt = parser.parse(time_str)
            return str(int(dt.timestamp()))
        except parser.ParserError:
            # 如果解析失败，返回1小时前作为默认值
            default_time = now - datetime.timedelta(hours=1)
            return str(int(default_time.timestamp()))
    
    def _format_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        格式化Prometheus API的响应结果
        """
        if "status" not in result or result["status"] != "success":
            return {
                "success": False,
                "error": result.get("error", "unknown error")
            }
        
        data = result.get("data", {})
        result_type = data.get("resultType", "")
        
        if result_type != "matrix":
            return {
                "success": True,
                "result_type": result_type,
                "raw_data": data
            }
        
        # 处理矩阵类型结果
        formatted_data = []
        for series in data.get("result", []):
            metric = series.get("metric", {})
            metric_name = metric.get("__name__", "unknown")
            
            # 收集标签
            labels = {key: value for key, value in metric.items() if key != "__name__"}
            
            # 收集数据点
            values = []
            for value_pair in series.get("values", []):
                if len(value_pair) >= 2:
                    timestamp, value = value_pair
                    try:
                        # 将时间戳转换为RFC3339格式
                        time_str = datetime.datetime.fromtimestamp(timestamp).isoformat()
                        # 尝试将值转换为数字
                        numeric_value = float(value)
                        values.append({
                            "timestamp": time_str,
                            "value": numeric_value
                        })
                    except (ValueError, TypeError):
                        # 对于无法转换的值，保留原样
                        values.append({
                            "timestamp": timestamp,
                            "value": value
                        })
            
            formatted_data.append({
                "metric": metric_name,
                "labels": labels,
                "values": values
            })
        
        return {
            "success": True,
            "result_type": "matrix",
            "data": formatted_data
        }
    
    def _create_markdown_table(self, result: Dict[str, Any]) -> Optional[str]:
        """
        将查询结果转换为Markdown表格格式，只显示每个指标最新的数据点，
        并将标签(labels)作为表格的列展示
        """
        if not result.get("success", False):
            return None
        
        if result.get("result_type") != "matrix":
            return None
        
        # 创建一个列表用于存储所有指标的最新数据点
        latest_data_points = []
        
        # 遍历每个时间序列
        for series in result.get("data", []):
            metric_name = series.get("metric", "unknown")
            labels = series.get("labels", {})
            values = series.get("values", [])
            
            if not values:
                continue
            
            # 找出最新的数据点（按timestamp排序）
            try:
                # 按timestamp对values进行排序
                sorted_values = sorted(values, key=lambda x: parser.parse(x.get("timestamp", "1970-01-01T00:00:00")), reverse=True)
                
                # 获取第一个(最新的)数据点
                if sorted_values:
                    latest_value = sorted_values[0]
                    
                    # 创建一个包含最新数据点的字典，加入标签信息
                    data_point = {
                        "timestamp": latest_value.get("timestamp", ""),
                        "value": latest_value.get("value", 0),
                        "metric": metric_name
                    }
                    
                    # 将标签添加到数据点中
                    for label_key, label_value in labels.items():
                        data_point[label_key] = label_value
                    
                    latest_data_points.append(data_point)
            except Exception as e:
                continue
        
        if not latest_data_points:
            return "no data found"
        
        # 创建DataFrame
        df = pd.DataFrame(latest_data_points)
        
        # 合并相同指标的不同实例
        grouped_data = []
        metrics = set(df["metric"].tolist())
        
        for metric in metrics:
            metric_df = df[df["metric"] == metric]
            
            # 使用to_markdown()生成该指标的Markdown表格
            try:
                # 选择要显示的列：timestamp、labels、value
                # 首先找出所有标签列（排除timestamp、value和metric）
                all_columns = set(metric_df.columns)
                exclude_columns = {"timestamp", "value", "metric"}
                label_columns = list(all_columns - exclude_columns)
                
                # 按照要求的顺序排列列
                display_columns = ["timestamp"] + label_columns + ["value"]
                
                # 选择列并生成表格
                table_df = metric_df[display_columns].copy()  # 创建明确的副本
                
                # 格式化timestamp列
                try:
                    table_df["timestamp"] = table_df["timestamp"].apply(
                        lambda ts: parser.parse(ts).strftime('%Y-%m-%dT%H:%M:%S')
                    )
                except Exception:
                    pass
                
                # 生成表格
                table = table_df.to_markdown(index=False)
                
                grouped_data.append(f"{table}")
            except Exception as e:
                grouped_data.append(f"### {metric}\n\ncannot generate table: {str(e)}")
        
        # 合并所有表格
        if grouped_data:
            return "\n\n".join(grouped_data)
        
        return None
