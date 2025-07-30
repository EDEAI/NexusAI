from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import pandas as pd

class Excel2JsonTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        file_meta = tool_parameters['file']
        try:
            df = pd.read_excel(file_meta.url, dtype=str)
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")

        yield self.create_text_message(df.to_json(orient="records", force_ascii=False))
