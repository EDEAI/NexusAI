from collections.abc import Generator
from typing import Any
from datetime import date, datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import json 
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class SqlDbTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_uri = tool_parameters.get("db_uri") or self.runtime.credentials.get("db_uri")
        sql_query = tool_parameters.get("sql_query").strip()
        format = tool_parameters.get("format", "json")
        try:
            
            engine = create_engine(db_uri)
            
            with engine.connect() as connection:
                result = connection.execute(text(sql_query))
                
               
                columns = result.keys()
 
                rows = [dict(zip(columns, row)) for row in result.fetchall()]
                if format == 'json':
                    yield self.create_json_message({
                        "columns": list(columns),
                        "rows": rows,
                    })
                elif format == 'json rows arr':
                    rows_arr = []
                    for row in rows:
                        row_values = []
                        for col in columns:
                            value = row[col]
                            if isinstance(value, (date, datetime)):
                                value = value.isoformat()
                            row_values.append(value)
                        rows_arr.append(row_values)
                    yield self.create_json_message({
                        "columns": list(columns),
                        "rows": rows_arr
                    })
                elif format == 'Markdown to string':
                    
                    result = f"```sql\n{sql_query}\n```\n\n"
                    result += "| " + " | ".join(columns) + " |\n"
                    result += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                    for row in rows:
                        result += "| " + " | ".join([str(value) for value in row.values()]) + " |\n"
                    yield self.create_text_message(result)
                elif format == 'Markdown to file':
                   
                    result = f"```sql\n{sql_query}\n```\n\n"
                    result += "| " + " | ".join(columns) + " |\n"
                    result += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                    for row in rows:
                        result += "| " + " | ".join([str(value) for value in row.values()]) + " |\n"
                    yield self.create_blob_message(result, meta={'mime_type': 'text/markdown', 'filename':'result.md'})
                elif format == 'csv':
                    result = f"{','.join(columns)}\n"
                    for row in rows:
                        result += ",".join([str(value) for value in row.values()]) + "\n"
                    yield self.create_blob_message(result, meta={'mime_type': 'text/csv', 'filename': 'result.csv'})
                elif format == 'yaml to file':
                    
                    result = "---\n"  
                    result += "columns:\n"
                    for col in columns:
                        result += f"  - {col}\n"
                    result += "rows:\n"
                    for row in rows:
                        result += "  - \n"
                        for key, value in row.items():
                            result += f"    {key}: {value}\n"
                    yield self.create_blob_message(result, meta={'mime_type': 'text/yaml', 'filename': 'result.yaml'})
                elif format == 'yaml to string':
                    result = "---\n"  
                    result += "columns:\n"
                    for col in columns:
                        result += f"  - {col}\n"
                    result += "rows:\n"
                    for row in rows:
                        result += "  - \n"
                        for key, value in row.items():
                            result += f"    {key}: {value}\n"
                    yield self.create_text_message(result)
                elif format == 'xlsx to file':
                   
                    result = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>\n"
                   
                    result += "  <tr style='background-color: #f2f2f2;'>\n"
                    for col in columns:
                        result += f"    <th style='border: 1px solid #ddd; padding: 8px;'>{col}</th>\n"
                    result += "  </tr>\n"
                    
                    for row in rows:
                        result += "  <tr>\n"
                        for value in row.values():
                            result += f"    <td style='border: 1px solid #ddd; padding: 8px;'>{str(value)}</td>\n"
                        result += "  </tr>\n"
                    result += "</table>"
                    yield self.create_blob_message(result, meta={'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': 'result.xlsx'})
                elif format == 'xlsx to string':
                    
                    result = "<table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse;'>\n"
                    
                    result += "  <tr style='background-color: #f2f2f2;'>\n"
                    for col in columns:
                        result += f"    <th style='border: 1px solid #ddd; padding: 8px;'>{col}</th>\n"
                    result += "  </tr>\n"
                    
                    for row in rows:
                        result += "  <tr>\n"
                        for value in row.values():
                            result += f"    <td style='border: 1px solid #ddd; padding: 8px;'>{str(value)}</td>\n"
                        result += "  </tr>\n"
                    result += "</table>"
                    yield self.create_text_message(result)
                elif format == 'html to file':
                    
                    result = "<table border='1'>\n"
                   
                    result += "  <tr>\n"
                    for col in columns:
                        result += f"    <th>{col}</th>\n"
                    result += "  </tr>\n"
                    
                    for row in rows:
                        result += "  <tr>\n"
                        for value in row.values():
                            result += f"    <td>{str(value)}</td>\n"
                        result += "  </tr>\n"
                    result += "</table>"
                elif format == 'html to string':
                    
                    result = "<table border='1'>\n"
                   
                    result += "  <tr>\n"
                    for col in columns:
                        result += f"    <th>{col}</th>\n"
                    result += "  </tr>\n"
                    
                    for row in rows:
                        result += "  <tr>\n"
                        for value in row.values():
                            result += f"    <td>{str(value)}</td>\n"
                        result += "  </tr>\n"
                    result += "</table>"    
                    yield self.create_text_message(result)
                else:
                    raise ValueError(f"Unsupported format: {format}")                

            
                connection.close()
                
        except SQLAlchemyError as e:
            yield ValueError(f"SQLAlchemyError: {e}")
