from collections.abc import Generator
from typing import Any
from datetime import datetime, timedelta

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from aliyun.log import LogClient
from aliyun.log.getlogsrequest import GetLogsRequest

from dify_plugin.errors.model import (
    InvokeServerUnavailableError,
)


class AliyunSlsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 获取查询参数
        query = tool_parameters.get('query', '').strip()
        project = tool_parameters.get('project', '').strip()
        logstore = tool_parameters.get('logstore', '').strip()
        from_time = tool_parameters.get('from_time', '').strip()
        to_time = tool_parameters.get('to_time', '').strip()
        limit = tool_parameters.get('limit', 100)
        endpoint = tool_parameters.get('endpoint', '').strip()
        access_key_id = tool_parameters.get('access_key_id', '').strip()
        access_key_secret = tool_parameters.get('access_key_secret', '').strip()

        if not endpoint:
            endpoint = self.runtime.credentials.get('endpoint', '')
        if not access_key_id:
            access_key_id = self.runtime.credentials.get('access_key_id', '')
        if not access_key_secret:
            access_key_secret = self.runtime.credentials.get('access_key_secret', '')
        
        if not endpoint or not access_key_id or not access_key_secret:
            yield self.create_text_message("错误：未指定endpoint、access_key_id或access_key_secret，请在查询参数或凭证中提供")
            return
        
        # 如果未指定project，则使用凭证中的project
        if not project:
            project = self.runtime.credentials.get('project', '')
        
        # 如果未指定logstore，则使用凭证中的logstore（如果存在）
        if not logstore and 'logstore' in self.runtime.credentials and self.runtime.credentials['logstore']:
            logstore = self.runtime.credentials.get('logstore', '')
        
        if not logstore:
            yield self.create_text_message("错误：未指定logstore，请在查询参数或凭证中提供logstore")
            return

        # 处理时间范围
        now = datetime.now()
        if not from_time:
            # 默认查询过去60分钟的日志
            from_time_obj = now - timedelta(minutes=60)
        else:
            try:
                # 尝试解析用户提供的时间
                from_time_obj = datetime.fromisoformat(from_time) # 2025-03-05 10:00:00
            except ValueError:
                # 如果解析失败，使用默认值
                from_time_obj = now - timedelta(minutes=60)
                
        if not to_time:
            to_time_obj = now
        else:
            try:
                to_time_obj = datetime.fromisoformat(to_time) # 2025-03-05 10:00:00
            except ValueError:
                to_time_obj = now
        
        # 转换为Unix时间戳（秒）
        from_time_unix = int(from_time_obj.timestamp())
        to_time_unix = int(to_time_obj.timestamp())
        
        try:
            # 创建LogClient
            client = LogClient(endpoint, access_key_id, access_key_secret)

            # 创建查询请求
            request = GetLogsRequest(project, logstore, from_time_unix, to_time_unix, query=query, line=limit, offset=0)
            
            # 执行查询
            response = client.get_logs(request)

            # 处理结果
            logs = response.get_logs()
            count = response.get_count()

            logs_list = []
            for log in logs:
                logs_list.append(log.get_contents())
        
            # 构建结果消息
            result = {
                "total": count,
                "query": query,
                "project": project,
                "logstore": logstore,
                "time_range": {
                    "from": from_time_obj.isoformat(),
                    "to": to_time_obj.isoformat()
                },
                "logs": logs_list
            }
            
            # 返回JSON格式的结果
            yield self.create_json_message(result)
            
            # 将日志数据格式化为Markdown表格
            markdown_table = self._format_logs_to_markdown(logs_list, count)
            
            # 返回Markdown格式的结果
            yield self.create_text_message(markdown_table)
            
        except Exception as e:
            # 处理所有异常
            raise InvokeServerUnavailableError(f"查询过程中发生错误：{str(e)}") from e
            
    def _format_logs_to_markdown(self, logs_list, count):
        """
        将日志数据格式化为Markdown表格
        """
        # 创建表头
        markdown = f""
        if count == 0:
            return markdown
            
        # 获取所有日志中的字段名称
        all_fields = set()
        for log in logs_list:
            all_fields.update(log.keys())

        # 过滤掉__tag__开头的字段
        all_fields = [field for field in all_fields if not field.startswith('__tag__') and not field.startswith('__topic__') and not field.startswith('__source__')]
        
        # 选择要显示的字段（优先显示常见的重要字段）
        priority_fields = ['time', 'level', 'message', 'content', 'timestamp', '__time__', ]
        display_fields = []
        
        # 先添加优先字段（如果存在）
        for field in priority_fields:
            if field in all_fields:
                display_fields.append(field)
                all_fields.remove(field)
        
        # 再添加剩余字段（按字母顺序）
        display_fields.extend(sorted(list(all_fields)))
        
        # 如果字段太多，只显示前50个
        if len(display_fields) > 50:
            display_fields = display_fields[:50]
            truncated = True
        else:
            truncated = False
        
        # 创建表头
        markdown += "| " + " | ".join(display_fields) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(display_fields)) + " |\n"
        
        # 添加表格内容
        for log in logs_list:
            row = []
            for field in display_fields:
                value = log.get(field, "")
                # 处理复杂类型和长文本
                if isinstance(value, (dict, list)):
                    value = str(value)
                if isinstance(value, str) and len(value) > 1000:
                    value = value[:997] + "..."
                # 转义Markdown表格中的竖线
                value = str(value).replace("|", "\\|")
                row.append(value)
            markdown += "| " + " | ".join(row) + " |\n"
        
        if truncated:
            markdown += "\n*注: 由于字段较多，只显示了前50个字段*\n"
        
        return markdown