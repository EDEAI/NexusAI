from collections.abc import Generator
from typing import Any
import json

from sqlalchemy import create_engine, inspect
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class QueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        db_uri = tool_parameters.get("db_uri") or self.runtime.credentials.get("db_uri")
        if not db_uri:
            raise ValueError("Database URI is not provided.")
        config_options = tool_parameters.get("config_options") or "{}"
        try:
            config_options = json.loads(config_options)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format for Connect Config")
        engine = create_engine(db_uri, **config_options)
        inspector = inspect(engine)

        tables = tool_parameters.get("tables")
        schema = tool_parameters.get("schema")
        if not schema:
            # sometimes the schema is empty string, it must be None
            schema = None
        tables = tables.split(",") if tables else inspector.get_table_names(schema=schema)

        schema_info = {}
        with engine.connect() as _:
            for table_name in tables:
                # Basic table info
                table_info = {
                    "table_name": table_name,
                    "columns": [],
                    "primary_keys": inspector.get_pk_constraint(table_name, schema=schema).get('constrained_columns', []),
                    "foreign_keys": [],
                    "indexes": []
                }
                
                # Get table comment
                try:
                    table_info["comment"] = inspector.get_table_comment(table_name, schema=schema).get('text', '')
                except NotImplementedError:
                    table_info["comment"] = ""
                
                # Get foreign keys
                try:
                    for fk in inspector.get_foreign_keys(table_name, schema=schema):
                        table_info["foreign_keys"].append({
                            "referred_table": fk['referred_table'],
                            "referred_columns": fk['referred_columns'],
                            "constrained_columns": fk['constrained_columns']
                        })
                except NotImplementedError:
                    pass
                
                # Get indexes
                try:
                    for idx in inspector.get_indexes(table_name, schema=schema):
                        table_info["indexes"].append({
                            "name": idx['name'],
                            "columns": idx['column_names'],
                            "unique": idx['unique']
                        })
                except NotImplementedError:
                    pass
                
                # Get columns
                try:
                    columns = inspector.get_columns(table_name, schema=schema)
                    table_info["columns"] = [
                        {
                            "name": col["name"],
                            "type": str(col["type"]),
                            "nullable": col.get("nullable", True),
                            "default": col.get("default"),
                            "comment": col.get("comment", ""),
                        }
                        for col in columns
                    ]
                    
                    schema_info[table_name] = table_info
                except Exception as e:
                    schema_info[table_name] = f"Error getting schema: {str(e)}"
        yield self.create_text_message(json.dumps(schema_info, ensure_ascii=False))
