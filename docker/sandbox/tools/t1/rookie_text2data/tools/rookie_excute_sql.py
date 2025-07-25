from dify_plugin import Tool
from typing import Any, Optional
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.alchemy_db_client import execute_sql
import json
from datetime import datetime, date
from decimal import Decimal
import csv
from io import StringIO
import re

class RookieExecuteSqlTool(Tool):
    RISK_KEYWORDS = {"DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"}
    SUPPORTED_FORMATS = {"json", "csv", "html", "text"}

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # 参数校验和预处理
            execute_params, result_format = self._validate_and_prepare_params(tool_parameters)
            
            # 执行 SQL
            result = execute_sql(**execute_params)
            
            # 处理结果格式
            yield from self._handle_result_format(
                result, 
                result_format,
                execute_params.get('schema')
            )
            
        except Exception as e:
            raise ValueError(f"数据库操作失败：{str(e)}")

    def _validate_and_prepare_params(self, params: dict) -> dict:
        """参数验证和预处理"""
        required_params = ['sql', 'db_type', 'host', 'port', 'db_name', 'username', 'password']
        missing = [p for p in required_params if not params.get(p)]
        if missing:
            raise ValueError(f"缺少必要参数: {', '.join(missing)}")

        try:
            port = int(params['port'])
        except ValueError:
            raise ValueError("端口号必须是整数")

        if self._contains_risk_commands(params['sql']):
            raise ValueError("SQL语句包含危险操作")

        # 数据库执行参数
        execute_params = {
            'db_type': params['db_type'],
            'host': params['host'],
            'port': port,
            'database': params['db_name'],
            'username': params['username'],
            'password': params['password'],
            'sql': params['sql'],
            'params': {},
            'schema': params.get('schema')
        }

        # 结果格式参数
        result_format = params.get('result_format', 'text').lower()

        return execute_params, result_format

    def _handle_result_format(self, result: Any, fmt: str, schema: Optional[str]) -> Generator[ToolInvokeMessage, None, None]:
        """处理不同格式的结果输出"""
        if fmt not in self.SUPPORTED_FORMATS:
            raise ValueError(f"不支持的格式: {fmt}。支持格式: {', '.join(self.SUPPORTED_FORMATS)}")

        # 处理空结果
        if self._is_empty_result(result):
            yield self.create_text_message("未查询到数据")
            return

        try:
            if fmt == 'json':
                yield self._handle_json(result)
            elif fmt == 'csv':
                yield from self._handle_csv(result)
            elif fmt == 'html':
                yield from self._handle_html(result)
            else:
                yield self._handle_text(result, schema)
        except Exception as e:
            raise ValueError(f"结果格式化失败: {str(e)}")

    def _handle_json(self, data: Any) -> ToolInvokeMessage:
        """生成JSON格式消息"""
        return self.create_json_message({
            "status": "success",
            "result": self._safe_serialize(data)
        })

    def _handle_text(self, data: Any, schema: Optional[str]) -> ToolInvokeMessage:
        """生成可读文本消息"""
        readable_text = self._to_readable_text(data, schema)
        return self.create_text_message(readable_text)

    def _handle_html(self, data: list[dict]) -> Generator[ToolInvokeMessage, None, None]:
        """生成HTML表格"""
        html_table = self._generate_html_table(data)
        yield self.create_blob_message(
            html_table.encode('utf-8'),
            meta={'mime_type': 'text/html', 'filename': 'result.html'}
        )

    def _handle_csv(self, data: list[dict]) -> Generator[ToolInvokeMessage, None, None]:
        """生成CSV文件"""
        output = StringIO()
        writer = csv.writer(output)
        
        # 写入表头
        if data:
            writer.writerow(data[0].keys())
        
        # 写入数据行
        for row in data:
            processed_row = [self._custom_serializer(val) for val in row.values()]
            writer.writerow(processed_row)

        yield self.create_blob_message(
            output.getvalue().encode('utf-8-sig'),
            meta={
                'mime_type': 'text/csv',
                'filename': 'result.csv',
                'encoding': 'utf-8-sig'
            }
        )

    def _generate_html_table(self, data: list[dict]) -> str:
        """生成标准HTML表格"""
        html = ["<table class='table table-bordered table-striped'>"]
        html.append("<thead><tr>")
        
        if data:
            html.extend(f"<th>{key}</th>" for key in data[0].keys())
        
        html.append("</tr></thead><tbody>")
        
        for row in data:
            html.append("<tr>")
            html.extend(f"<td>{self._custom_serializer(val)}</td>" for val in row.values())
            html.append("</tr>")
        
        html.append("</tbody></table>")
        return "".join(html)

    def _to_readable_text(self, data: Any, schema: Optional[str]) -> str:
        """生成可读性文本"""
        if schema:
            header = f"Schema: {schema}\n"
        else:
            header = ""

        if isinstance(data, list):
            return header + "\n".join(
                json.dumps(row, ensure_ascii=False, indent=2, default=self._custom_serializer)
                for row in data
            )
        return header + json.dumps(data, indent=2, ensure_ascii=False, default=self._custom_serializer)

    def _contains_risk_commands(self, sql: str) -> bool:
        """增强的SQL注入检测"""
        cleaned_sql = re.sub(r'/\*.*?\*/|--.*', '', sql, flags=re.DOTALL)
        statements = [s.strip() for s in cleaned_sql.split(';') if s.strip()]
        
        for stmt in statements:
            first_token = re.search(r'\b(\w+)\b', stmt, re.IGNORECASE)
            if first_token and first_token.group(1).upper() in self.RISK_KEYWORDS:
                return True
        return False

    def _is_empty_result(self, result: Any) -> bool:
        """判断是否为空结果"""
        if result is None:
            return True
        if isinstance(result, list) and not result:
            return True
        if isinstance(result, dict) and result.get("rowcount", 0) == 0:
            return True
        return False

    def _custom_serializer(self, obj: Any) -> Any:
        """增强的数据类型序列化"""
        if isinstance(obj, (datetime, date)):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        return str(obj)

    def _safe_serialize(self, data: Any) -> Any:
        """安全的数据序列化"""
        return json.loads(
            json.dumps(data, default=self._custom_serializer, ensure_ascii=False)
        )