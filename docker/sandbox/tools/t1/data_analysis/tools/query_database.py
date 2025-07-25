from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from utils.digitforce_api import DigitForceApi
import pandas as pd
from io import BytesIO
import re
from urllib.parse import quote


class QueryDatabase(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            print(tool_parameters)
            api_key = self.runtime.credentials["digitforce_api_key"]
            query = tool_parameters['query']
            database_type = tool_parameters['database_type']
            database_leixing = tool_parameters['database_leixing']
            user = quote(tool_parameters['user'])
            password = quote(tool_parameters['password'])
            IP = quote(str(tool_parameters['IP']))
            port = quote(str(tool_parameters['port']))
            db_name = quote(str(tool_parameters['db_name']))
            if database_leixing == 'mysql':
                database_leixing = 'mysql+pymysql'
                url = f"{database_leixing}://{user}:{password}@{IP}:{port}/{db_name}?charset=utf8"
            elif database_leixing == 'postgresql':
                database_leixing = 'postgresql+psycopg2'
                url = f"{database_leixing}://{user}:{password}@{IP}:{port}/{db_name}?client_encoding=utf8"
            elif database_leixing == 'oracle':
                database_leixing = 'oracle+cx_oracle'
                service_name = f"?service_name={db_name}" if service_name else f"/{db_name}"
                url = f"{database_leixing}://{user}:{password}@{IP}:{port}{service_name}?charset=UTF8"
            elif database_leixing == 'sqlserver':
                database_leixing = 'mssql+pyodbc'
                url = f"{database_leixing}://{user}:{password}@{IP}:{port}/{db_name}?driver=ODBC+Driver+17+for+SQL+Server&charset=utf8"
            elif database_leixing == 'mongodb':
                database_leixing = 'mongodb+pymongo'
                url = f"{database_leixing}://{user}:{password}@{IP}:{port}/{db_name}"
            

            print(tool_parameters)

            if len(query) > 10000:
                yield self.create_text_message("The query is too long. Please check if you have entered any incorrect variables")
            result = DigitForceApi(api_key).dify_api_post(
                {"query":query,
                 "url":url,
                 "database_type":database_type
                },"QueryDatabase")
            if result:
                yield self.create_text_message(result)
            else:
                yield self.create_text_message("Result is empty.Possible data source or code generation issue. Check input data and retry.")
            if re.search(r'SELECT', result, re.IGNORECASE):#判断是否为数据库输入，若是则去掉前面sql语句
                    match = re.search(r'(\|.+\|(?:\n\|.*\|)+)', result, re.DOTALL)
 
                    if match:
                        result=match.group(1)
            print(result)
            try:
                tables_md = [tbl for tbl in result.split('\n\n') if tbl.strip().startswith('|')]
                tables = []
                for tbl_md in tables_md:
                    lines = [line for line in tbl_md.splitlines() if line.strip().startswith('|')]
                    if len(lines) < 2:
                        continue
                    header = [h.strip() for h in lines[0].strip('|').split('|')]
                    rows = [
                        [cell.strip() for cell in row.strip('|').split('|')]
                        for row in lines[2:]
                    ]
                    df = pd.DataFrame(rows, columns=header)
                    tables.append(df)
                if tables:
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        for idx, df in enumerate(tables):
                            sheet_name = f"Sheet{idx+1}"
                            df.to_excel(writer, index=False, sheet_name=sheet_name)
                    output.seek(0)
                    yield self.create_blob_message(
                        blob=output.getvalue(),
                        meta={
                            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            "file_name": "query_result.xlsx"
                        }
                    )
                    output.close()
            except Exception as e:
                yield self.create_text_message(f"excel download error: {str(e)}")
        except Exception as e:
            yield self.create_text_message(str(e))