from dify_plugin import Tool
from typing import Any
from collections.abc import Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.alchemy_db_client import execute_sql
import json
from datetime import datetime, date
from decimal import Decimal
import csv
from io import StringIO

class HologresExcuteSqlTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Get the SQL statement passed in
        sql = tool_parameters.get("sql")
        if not sql:
            raise ValueError("SQL statement cannot be empty")
        
        # Improved risk detection
        if self._contains_risk_commands(sql):
            raise ValueError("SQL statement contains risks")

        # Get database connection parameters
        db_type = tool_parameters.get("db_type")
        host = tool_parameters.get("host")
        port = tool_parameters.get("port")
        database = tool_parameters.get("db_name")
        username = tool_parameters.get("username")
        password = tool_parameters.get("password")

        if not all([db_type, host, port, database, username, password]):
            raise ValueError("Database connection parameters cannot be empty")
        
        try:
            # Execute SQL statement (query or non-query)
            result = execute_sql(
                db_type, host, int(port), database, 
                username, password, sql, ""
            )
            # Handle empty results
            if isinstance(result, list) and not result:  # Empty query result
                yield self.create_text_message("No data found")
            elif isinstance(result, dict) and "rowcount" in result and result["rowcount"] == 0:  # No affected rows
                yield self.create_text_message("No data affected")

            result_format = tool_parameters.get("result_format", "json")
            
            if result_format == 'json':
                yield self.create_json_message({
                        "status": "success",
                        "result": result
                    }  
                )
            elif result_format == 'csv':
                yield from self._handle_csv(result)
            elif result_format == 'html':
                yield from self._handle_html(result)
            else:
                if result is not None:
                    message_text = json.dumps(
                        result, 
                        ensure_ascii=False, 
                        default=self._custom_serializer  # Key modification point
                    )
                else:
                    message_text = "No data found"
                yield self.create_text_message(message_text)
        except Exception as e:
            raise ValueError(f"Database operation failed: {str(e)}")

    def _handle_html(self, data: list[dict[str, Any]] | dict[str, Any] | None) -> Generator[ToolInvokeMessage, None, None]:
        """Generate HTML table message"""
        html_table = self._to_html_table(data)
        yield self.create_blob_message(html_table.encode('utf-8'), meta={'mime_type': 'text/html', 'filename': 'result.html'})

    def _handle_csv(self, data: list[dict[str, Any]] | dict[str, Any] | None) -> Generator[ToolInvokeMessage]:
        """Generate CSV file message"""
        output = StringIO()
        # Write BOM (only first 3 bytes)
        output.write('\ufeff')  # Add BOM
        writer = csv.writer(output)
        # Write header
        writer.writerow(data[0].keys())
        
        # Write data rows (handle date serialization)
        for row in data:
            processed_row = [
                self._custom_serializer(val) if isinstance(val, (date, datetime)) else val
                for val in row.values()
            ]
            writer.writerow(processed_row)

        # Note: utf-8-sig encoding automatically includes BOM, recommended to use this method
        yield self.create_blob_message(
            output.getvalue().encode('utf-8-sig'),  # Key modification point ✅
            meta={
                'mime_type': 'text/csv',
                'filename': 'result.csv',
                'encoding': 'utf-8-sig'  # Explicitly declare encoding
            }
        )
    
    def _to_html_table(self, data: list[dict]) -> str:
        """Generate standard HTML table"""
        html = ["<table border='1'>"]
        html.append("<tr>" + "".join(f"<th>{col}</th>" for col in data[0].keys()) + "</tr>")
        
        for row in data:
            html.append(
                "<tr>" + 
                "".join(f"<td>{self._custom_serializer(val)}</td>" for val in row.values()) + 
                "</tr>"
            )
        
        html.append("</table>")
        return "".join(html)

    def _contains_risk_commands(self, sql: str) -> bool:
        import re
        risk_keywords = {"DROP", "DELETE", "TRUNCATE", "ALTER", "UPDATE", "INSERT"}
        # Remove comments
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        sql = re.sub(r'--.*', '', sql)
        # Split statements
        statements = re.split(r';\s*', sql)
        for stmt in statements:
            stmt = stmt.strip()
            if not stmt:
                continue
            # Match first word (case insensitive)
            match = re.match(r'\s*([^\s]+)', stmt, re.IGNORECASE)
            if match:
                first_word = match.group(1).upper()
                if first_word in risk_keywords:
                    return True
        return False
    
    def _custom_serializer(self, obj: Any) -> Any:
        """Handle common non-serializable database types"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()  # Convert to ISO8601 string
        elif isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float
        # Add other types that need to be handled (such as bytes)
        raise TypeError(f"Unserializable type {type(obj)}")
