from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import pandas as pd
from io import StringIO, BytesIO

class Json2ExcelTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        json_str = tool_parameters['json_str']
        try:
            df = pd.read_json(StringIO(json_str))
        except Exception as e:
            raise Exception(f"Error reading JSON string: {str(e)}")

        # convert df to excel bytes
        excel_buffer = BytesIO()
        try:
            df.to_excel(excel_buffer, index=False)
            excel_buffer.seek(0)
        except Exception as e:
            raise Exception(f"Error converting DataFrame to Excel: {str(e)}")

        # create a blob with the excel bytes
        try:
            excel_bytes = excel_buffer.getvalue()
            filename = tool_parameters.get('filename', 'Converted Data')
            filename = f"{filename.replace(' ', '_')}.xlsx"

            yield self.create_text_message(f"Excel file '{filename}' generated successfully")

            yield self.create_blob_message(
                    blob=excel_bytes,
                    meta={
                        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "filename": filename
                    }
                )
        except Exception as e:
            raise Exception(f"Error creating Excel file message: {str(e)}")
