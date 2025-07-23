from collections.abc import Generator
from typing import Any
import io

import pandas as pd
from sqlalchemy import create_engine
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class CSVQueryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file = tool_parameters.get("file")
        if file.extension != ".csv":
            raise ValueError("Only CSV files are supported.")
        query = tool_parameters.get("query")
        df = pd.read_csv(io.BytesIO(file.blob))
        engine = create_engine("sqlite:///csv.db")
        df.to_sql("csv", engine, index=False, if_exists='replace')
        format = tool_parameters.get("format")
        
        try:
            result_df = pd.read_sql_query(query, engine)

            if format == "json":
                json_data = result_df.to_dict(orient='records')
                yield self.create_json_message({"result": json_data})
            else:
                markdown_table = (
                    "| " + " | ".join(result_df.columns) + " |\n" +
                    "| " + " | ".join(["---"] * len(result_df.columns)) + " |\n" +
                    "\n".join("| " + " | ".join(str(x) for x in row) + " |" 
                            for row in result_df.values)
                )
                yield self.create_text_message(markdown_table)
        finally:
            engine.dispose()
