from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import httpx

import snowflake.connector
import pandas as pd
from decimal import Decimal

class SQLTool(Tool):
    def __init__(self, runtime, session):
        super().__init__(runtime, session)
        self.conn = None
        self._connect()

    def __del__(self):
        super().__del__()
        if self.conn:
            try:
                self.conn.close()
            except Exception as e:
                pass

    def _connect(self):
        if not self.runtime.credentials.get("pat"):
            try:
                self.conn = snowflake.connector.connect(
                    account=self.runtime.credentials.get("account"),
                    user=self.runtime.credentials.get("user"),
                    password=self.runtime.credentials.get("password"),
                    warehouse=self.runtime.credentials.get("warehouse", None),
                    role=self.runtime.credentials.get("role", None),
                )
            except Exception as e:
                self.conn = None
                self.conn_error = str(e)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        if self.runtime.credentials.get("pat"):
            if not self.runtime.credentials.get("account"):
                yield self.create_text_message("Account is required for PAT authentication.")
                
            endpoint = "https://{account}.snowflakecomputing.com/api/v2/statements".format(
                account=self.runtime.credentials.get("account")
            )
            try:
                response = httpx.post(
                    endpoint,
                    headers={
                        'Authorization' : 'Bearer {}'.format(self.runtime.credentials.get("pat")),
                        'Content-Type' : 'application/json'
                    },
                    json={
                        "statement": tool_parameters.get("query", None),
                    },
                    timeout=60,
                )
                if response.status_code == 200:
                    json_data = response.json()
                    if "data" in json_data:
                        data = self._parse_response(json_data)
                        df = pd.DataFrame(data)

                        yield self.create_json_message(df.to_dict(orient='list'))

                    else:
                        yield self.create_text_message("No data found in the response.")
                else:
                    yield self.create_text_message(f"Error: {response.status_code} - {response.text}")
            except Exception as e:
                yield self.create_text_message(f"Exception: {str(e)} - {response.text}")
        else:
            if not self.conn:
                yield self.create_text_message("Connection error: {}".format(self.conn_error))
                return
            try:
                query = tool_parameters.get("query", None)
                if query:
                    cursor = self.conn.cursor()
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    cols = [col.name for col in cursor.description]
                    data = [dict(zip(cols, row)) for row in rows]

                    df = pd.DataFrame(data)
                    df = df.map(lambda x: x if not isinstance(x, Decimal) else float(x))

                    cursor.close()

                    yield self.create_json_message(df.to_dict(orient='list'))
            except Exception as e:
                yield self.create_text_message(str(e))

    def _parse_response(self,response):
        metadata = response['resultSetMetaData']['rowType']
        data = response['data']
        column_names = [col['name'] for col in metadata]
        column_types = [col['type'].lower() for col in metadata]
        column_scales = [col.get('scale', 0) for col in metadata]

        parsed_data = []
        for row in data:
            parsed_row = {}
            for idx, value in enumerate(row):
                col_type = column_types[idx]
                scale = column_scales[idx]
                if value is None:
                    parsed_value = None
                elif col_type == 'fixed':
                    if scale == 0:
                        parsed_value = int(value)
                    else:
                        parsed_value = float(value)
                elif col_type == 'boolean':
                    parsed_value = value.lower() == 'true'
                else:
                    parsed_value = value
                parsed_row[column_names[idx]] = parsed_value
            parsed_data.append(parsed_row)
        return parsed_data
        