from collections.abc import Generator
from typing import Any, Dict, List
import datetime
import requests
import re
import pandas as pd
from dateutil import parser
import time
import traceback

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.model import InvokeServerUnavailableError


class KubernetesPodMetricsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取参数
        namespace = tool_parameters.get("namespace", "")
        selector = tool_parameters.get("selector", "")
        pod_name_pattern = tool_parameters.get("pod_name_pattern", "")
        
        # 获取时间范围参数
        start_time = tool_parameters.get("start_time", "1h")
        end_time = tool_parameters.get("end_time", "now")
        step = tool_parameters.get("step", "1m")
        
        # 获取Prometheus连接信息
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
        
        try:
            # 转换时间参数
            start_timestamp, end_timestamp = self._parse_time_range(start_time, end_time)
            
            # 获取Pod信息
            pod_data = self._get_pod_data(api_url, headers, namespace, selector, pod_name_pattern, 
                                          start_timestamp, end_timestamp, step)
            
            # 格式化为Markdown表格
            if pod_data:
                markdown_table = self._create_markdown_table(pod_data)
                yield self.create_text_message(markdown_table)
            else:
                yield self.create_text_message("no pod found")
            
        except Exception as e:
            traceback.print_exc()
            raise InvokeServerUnavailableError(f"get pod metrics error: {str(e)}") from e
            
    def _parse_time_range(self, start_time: str, end_time: str) -> tuple:
        """解析时间范围参数，支持相对时间和绝对时间"""
        # 处理结束时间
        if end_time.lower() == 'now':
            end_timestamp = int(time.time())
        else:
            # 尝试解析为绝对时间
            try:
                end_timestamp = int(parser.parse(end_time).timestamp())
            except:
                # 尝试解析为相对时间
                end_timestamp = int(time.time())
                
        # 处理开始时间
        try:
            # 尝试解析为绝对时间
            start_timestamp = int(parser.parse(start_time).timestamp())
        except:
            # 尝试解析为相对时间
            start_timestamp = self._parse_relative_time(start_time, end_timestamp)
            
        return start_timestamp, end_timestamp
    
    def _parse_relative_time(self, time_str: str, reference_time: int) -> int:
        """解析相对时间，如 1h, 2d, 3w 等"""
        units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
        }
        
        match = re.match(r'^(\d+)([smhdw])$', time_str)
        if match:
            value, unit = match.groups()
            seconds = int(value) * units[unit]
            return reference_time - seconds
        
        # 默认为1小时前
        return reference_time - 3600
            
    def _get_pod_data(self, api_url: str, headers: Dict[str, str], 
                     namespace: str, selector: str, pod_name_pattern: str,
                     start_timestamp: int, end_timestamp: int, step: str) -> List[Dict[str, Any]]:
        """获取Pod的资源使用数据"""
        result = []
        
        # 构建Pod查询表达式
        namespace_filter = f'namespace="{namespace}"' if namespace else ''
        selector_filter = ''
        if selector:
            # 将selector (key=value,key2=value2) 转换为Prometheus查询格式
            selectors = selector.split(',')
            for s in selectors:
                if '=' in s:
                    k, v = s.strip().split('=', 1)
                    selector_filter += f', {k}="{v}"'
        
        # 1. 获取pod列表 - 使用kube_pod_info指标
        pod_query = 'kube_pod_labels'
        if namespace_filter or selector_filter or pod_name_pattern:
            pod_query += '{' + namespace_filter

            if namespace_filter and selector_filter:
                pod_query += selector_filter
            if pod_name_pattern:
                if pod_query[-1] == '{':
                    pod_query += f'pod=~"{pod_name_pattern}"'
                else:
                    pod_query += f', pod=~"{pod_name_pattern}"'
            pod_query += '}'
            
        pod_data = self._query_prometheus(api_url, headers, pod_query)

        if not pod_data or not pod_data.get('data', {}).get('result', []):
            return result
        
        # 过滤pod名称
        pods = []
        for item in pod_data.get('data', {}).get('result', []):
            if len(pods) >= 20: # 限制最多查询20个pod
                break
            pod_name = item.get('metric', {}).get('pod', '')
            pod_namespace = item.get('metric', {}).get('namespace', '')
            node = item.get('metric', {}).get('node', '')
                
            pods.append({
                'name': pod_name,
                'namespace': pod_namespace,
                'node': node
            })
        
        # 2. 查询指定时间范围内的指标数据
        if pods:
            # 批量查询所有pod的CPU使用率
            pod_names = '|'.join([pod.get('name') for pod in pods])
            
            # 使用范围查询API获取时间序列数据
            # CPU使用率随时间变化
            cpu_query = f'sum(irate(container_cpu_usage_seconds_total{{pod=~"{pod_names}",container !="",container!="POD"}}[1m])) by (pod) / (sum(container_spec_cpu_quota{{pod=~"{pod_names}",container !="",container!="POD"}}/100000) by (pod)) * 100'
            cpu_range_data = self._query_prometheus_range(api_url, headers, cpu_query, 
                                                       start_timestamp, end_timestamp, step)
            
            # 内存使用率随时间变化
            memory_query = f'sum (container_memory_working_set_bytes{{pod=~"{pod_names}",container !="",container!="POD"}}) by (pod)/ sum(container_spec_memory_limit_bytes{{pod=~"{pod_names}",container !="",container!="POD"}}) by (pod) * 100'
            memory_range_data = self._query_prometheus_range(api_url, headers, memory_query, 
                                                         start_timestamp, end_timestamp, step)
            
            # 重启次数变化
            restart_query = f'sum by (pod) (kube_pod_container_status_restarts_total{{pod=~"{pod_names}"}})'
            restart_range_data = self._query_prometheus_range(api_url, headers, restart_query, 
                                                           start_timestamp, end_timestamp, step)
            
            # 查询其他即时指标
            cpu_request_query = f'sum by (pod) (kube_pod_container_resource_requests{{pod=~"{pod_names}",resource="cpu"}})'
            cpu_request_data = self._query_prometheus(api_url, headers, cpu_request_query)
            
            cpu_limit_query = f'sum by (pod) (kube_pod_container_resource_limits{{pod=~"{pod_names}",resource="cpu"}})'
            cpu_limit_data = self._query_prometheus(api_url, headers, cpu_limit_query)
            
            memory_request_query = f'sum by (pod) (kube_pod_container_resource_requests{{pod=~"{pod_names}",resource="memory"}})'
            memory_request_data = self._query_prometheus(api_url, headers, memory_request_query)
            
            memory_limit_query = f'sum by (pod) (kube_pod_container_resource_limits{{pod=~"{pod_names}",resource="memory"}})'
            memory_limit_data = self._query_prometheus(api_url, headers, memory_limit_query)
            
            phase_query = f'kube_pod_status_phase{{pod=~"{pod_names}",phase=~"Running|Pending|Failed|Succeeded|Unknown"}}'
            phase_data = self._query_prometheus(api_url, headers, phase_query)
            
            uptime_query = f'time() - kube_pod_start_time{{pod=~"{pod_names}"}}'
            uptime_data = self._query_prometheus(api_url, headers, uptime_query)
            
            # 处理数据
            for pod in pods:
                pod_name = pod['name']
                pod_stats = {'name': pod_name, 'namespace': pod['namespace'], 'node': pod['node']}
                
                # 处理CPU使用率时间序列数据
                if cpu_range_data and 'result' in cpu_range_data.get('data', {}):
                    for series in cpu_range_data['data']['result']:
                        if series.get('metric', {}).get('pod') == pod_name and series.get('values', []):
                            values = [float(v[1]) for v in series['values']]
                            pod_stats['cpu_usage_avg'] = round(sum(values) / len(values), 3) if values else 0
                            pod_stats['cpu_usage_max'] = round(max(values), 3) if values else 0
                            pod_stats['cpu_usage_min'] = round(min(values), 3) if values else 0
                            pod_stats['cpu_usage_curr'] = round(float(series['values'][-1][1]), 3) if series['values'] else 0
                
                # 处理内存使用率时间序列数据
                if memory_range_data and 'result' in memory_range_data.get('data', {}):
                    for series in memory_range_data['data']['result']:
                        if series.get('metric', {}).get('pod') == pod_name and series.get('values', []):
                            values = [float(v[1]) for v in series['values']]
                            pod_stats['memory_usage_avg'] = round(sum(values) / len(values), 3) if values else 0
                            pod_stats['memory_usage_max'] = round(max(values), 3) if values else 0
                            pod_stats['memory_usage_min'] = round(min(values), 3) if values else 0
                            pod_stats['memory_usage_curr'] = round(float(series['values'][-1][1]), 3) if series['values'] else 0
                
                # 处理重启次数变化
                if restart_range_data and 'result' in restart_range_data.get('data', {}):
                    for series in restart_range_data['data']['result']:
                        if series.get('metric', {}).get('pod') == pod_name and series.get('values', []):
                            if len(series['values']) > 1:
                                first_value = float(series['values'][0][1])
                                last_value = float(series['values'][-1][1])
                                pod_stats['restart_count_period'] = int(last_value - first_value)
                            pod_stats['restart_count_total'] = int(float(series['values'][-1][1])) if series['values'] else 0
                
                # 添加其他即时信息
                # CPU请求
                if cpu_request_data and 'result' in cpu_request_data.get('data', {}):
                    for item in cpu_request_data['data']['result']:
                        if item.get('metric', {}).get('pod') == pod_name and item.get('value', []):
                            pod_stats['cpu_request'] = float(item['value'][1])
                
                # CPU限制
                if cpu_limit_data and 'result' in cpu_limit_data.get('data', {}):
                    for item in cpu_limit_data['data']['result']:
                        if item.get('metric', {}).get('pod') == pod_name and item.get('value', []):
                            pod_stats['cpu_limit'] = float(item['value'][1])
                
                # 内存请求
                if memory_request_data and 'result' in memory_request_data.get('data', {}):
                    for item in memory_request_data['data']['result']:
                        if item.get('metric', {}).get('pod') == pod_name and item.get('value', []):
                            pod_stats['memory_request'] = round(float(item['value'][1]) / (1024 * 1024))  # 转换为MiB
                
                # 内存限制
                if memory_limit_data and 'result' in memory_limit_data.get('data', {}):
                    for item in memory_limit_data['data']['result']:
                        if item.get('metric', {}).get('pod') == pod_name and item.get('value', []):
                            pod_stats['memory_limit'] = round(float(item['value'][1]) / (1024 * 1024))  # 转换为MiB
                
                # Pod阶段状态
                if phase_data and 'result' in phase_data.get('data', {}):
                    for item in phase_data['data']['result']:
                        if (item.get('metric', {}).get('pod') == pod_name and 
                            item.get('value', []) and float(item['value'][1]) > 0):
                            pod_stats['phase'] = item.get('metric', {}).get('phase', 'Unknown')
                
                # Pod存活时间
                if uptime_data and 'result' in uptime_data.get('data', {}):
                    for item in uptime_data['data']['result']:
                        if item.get('metric', {}).get('pod') == pod_name and item.get('value', []):
                            uptime_seconds = float(item['value'][1])
                            # 转换为人类可读格式
                            if uptime_seconds < 3600:  # 小于1小时
                                pod_stats['uptime'] = f"{round(uptime_seconds / 60, 1)} 分钟"
                            elif uptime_seconds < 86400:  # 小于1天
                                pod_stats['uptime'] = f"{round(uptime_seconds / 3600, 1)} 小时"
                            else:  # 大于等于1天
                                pod_stats['uptime'] = f"{round(uptime_seconds / 86400, 1)} 天"
                
                # 添加查询时间范围信息
                start_dt = datetime.datetime.fromtimestamp(start_timestamp)
                end_dt = datetime.datetime.fromtimestamp(end_timestamp)
                pod_stats['query_period'] = f"{start_dt.strftime('%Y-%m-%d %H:%M')} 至 {end_dt.strftime('%Y-%m-%d %H:%M')}"
                
                result.append(pod_stats)
                
        return result
    
    def _query_prometheus(self, api_url: str, headers: Dict[str, str], query: str) -> Dict[str, Any]:
        """向Prometheus发送即时查询请求"""
        query_url = f"{api_url}/api/v1/query"
        params = {"query": query}
        
        response = requests.get(
            query_url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print("query prometheus response: ", response)
            return {}
        
        return response.json()
    
    def _query_prometheus_range(self, api_url: str, headers: Dict[str, str], 
                             query: str, start: int, end: int, step: str) -> Dict[str, Any]:
        """向Prometheus发送范围查询请求"""
        query_url = f"{api_url}/api/v1/query_range"
        params = {
            "query": query,
            "start": start,
            "end": end,
            "step": step
        }
        
        response = requests.get(
            query_url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code != 200:
            print("query prometheus response: ", response)
            return {}
        
        return response.json()
    
    def _create_markdown_table(self, pod_data: List[Dict[str, Any]]) -> str:
        """将Pod数据转换为Markdown表格"""
        if not pod_data:
            return "未找到符合条件的Pod"
        
        # 创建DataFrame
        df = pd.DataFrame(pod_data)
        
        # 对缺失数据进行适当处理
        df = df.fillna({
            'cpu_usage_avg': 0, 'cpu_usage_max': 0, 'cpu_usage_min': 0, 'cpu_usage_curr': 0,
            'memory_usage_avg': 0, 'memory_usage_max': 0, 'memory_usage_min': 0, 'memory_usage_curr': 0,
            'restart_count_period': 0, 'restart_count_total': 0,
            'cpu_request': 0, 'cpu_limit': 0,
            'memory_request': 0, 'memory_limit': 0,
            'phase': 'Unknown', 'uptime': 'N/A',
        })
        
        # 处理CPU使用率
        if 'cpu_usage_curr' in df.columns:
            df['cpu_usage'] = df['cpu_usage_curr'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理CPU使用率平均值
        if 'cpu_usage_avg' in df.columns:
            df['cpu_usage_avg'] = df['cpu_usage_avg'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理CPU使用率最大值
        if 'cpu_usage_max' in df.columns:
            df['cpu_usage_max'] = df['cpu_usage_max'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理CPU使用率最小值
        if 'cpu_usage_min' in df.columns:
            df['cpu_usage_min'] = df['cpu_usage_min'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理内存使用率
        if 'memory_usage_curr' in df.columns:
            df['memory_usage'] = df['memory_usage_curr'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理内存使用率平均值
        if 'memory_usage_avg' in df.columns:
            df['memory_usage_avg'] = df['memory_usage_avg'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理内存使用率最大值
        if 'memory_usage_max' in df.columns:
            df['memory_usage_max'] = df['memory_usage_max'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 处理内存使用率最小值
        if 'memory_usage_min' in df.columns:
            df['memory_usage_min'] = df['memory_usage_min'].apply(lambda x: f"{x:.4f}%" if pd.notnull(x) else "N/A")

        # 将内存值从MiB转换为适当的单位 (MiB 或 GiB)
        def format_memory(mem_value):
            if pd.isna(mem_value):
                return "N/A"
            if mem_value == 0:
                return "无限制"
            if mem_value >= 1024:
                return f"{round(mem_value/1024, 1)} GiB"
            else:
                return f"{round(mem_value)} MiB"
        
        # 处理CPU请求和限制
        def format_cpu(cpu_value):
            if pd.isna(cpu_value):
                return "N/A"
            if cpu_value == 0:
                return "无限制"
            else:
                return f"{round(cpu_value * 1000)}m"
        
        # 处理内存请求和限制
        if 'memory_request' in df.columns:
            df['memory_request'] = df['memory_request'].apply(format_memory)
        if 'memory_limit' in df.columns:
            df['memory_limit'] = df['memory_limit'].apply(format_memory)

        # 处理CPU请求和限制
        if 'cpu_request' in df.columns:
            df['cpu_request'] = df['cpu_request'].apply(format_cpu)
        if 'cpu_limit' in df.columns:
            df['cpu_limit'] = df['cpu_limit'].apply(format_cpu)
        
  
        # 选择要展示的列并排序（根据图片中的格式）
        columns = ['name', 'uptime', 'namespace', 'phase', 
                  'cpu_usage', 'cpu_usage_avg', 'cpu_usage_max', 'cpu_usage_min',
                  'memory_usage', 'memory_usage_avg', 'memory_usage_max', 'memory_usage_min',
                  'cpu_request', 'cpu_limit', 
                  'memory_request', 'memory_limit', 
                  'restart_count_total']
        
        # 调整列名显示
        column_rename = {
            'name': 'Pod名称',
            'uptime': '存活时长',
            'namespace': '命名空间',
            'phase': '状态',
            'cpu_usage': 'CPU使用率最近值',
            'cpu_usage_avg': 'CPU使用率平均值',
            'cpu_usage_max': 'CPU使用率最大值',
            'cpu_usage_min': 'CPU使用率最小值',
            'memory_usage': '内存使用率最近值',
            'memory_usage_avg': '内存使用率平均值',
            'memory_usage_max': '内存使用率最大值',
            'memory_usage_min': '内存使用率最小值',
            'cpu_request': 'CPU请求',
            'cpu_limit': 'CPU限制',
            'memory_request': '内存请求',
            'memory_limit': '内存限制',
            'restart_count_total': '24h重启次数'
        }
        
        # 选择可用列
        available_columns = [col for col in columns if col in df.columns]
        df = df[available_columns]
        
        # 重命名列
        df = df.rename(columns={k: column_rename[k] for k in available_columns if k in column_rename})
        
        # 生成Markdown表格
        markdown_table = f"### Kubernetes Pod资源使用情况\n\n"
        markdown_table += df.to_markdown(index=False)
        return markdown_table 