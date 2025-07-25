from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import requests
import json

class Pdf2markdownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:     
        Timeout = 600
        url_to_fetch = tool_parameters.get("url")
        app_id = tool_parameters.get("app_id")
        secret_code = tool_parameters.get("secret_code")
        options_str = tool_parameters.get("options")

        if options_str:
            try:
                options = json.loads(options_str.replace("'", '"')) if options_str else {}
            except json.JSONDecodeError:
                options = {}
        else:
            options = {}

        try:
            response = requests.get(url_to_fetch, timeout=Timeout)
            if response.status_code != 200:
                yield self.create_json_message({
                    "code": response.status_code,
                    "message": "Download file failed.",
                    "markdown": ""
                })
                return
            
            file_data = response.content

            api_url = 'https://api.textin.com/ai/service/v1/pdf_to_markdown?page_count=999&apply_document_tree=1'
            headers = {
                'x-ti-app-id': app_id,
                'x-ti-secret-code': secret_code
            }
            options['from'] = 'dify'
            response = requests.post(
                api_url,
                headers=headers,
                data=file_data,
                params=options,
                timeout=Timeout
            )

            if response.status_code != 200:
                yield self.create_json_message({
                    "code": response.status_code,
                    "message": response.text,
                    "markdown": ""
                })
                return

            json_data = response.json()
            if json_data.get("code") != 200:
                yield self.create_json_message({
                    "code": json_data.get("code"),
                    "message": json_data.get("message"),
                    "markdown": ""
                })
            else:
                yield self.create_json_message(response.json())
                
        except Exception as e:
            yield self.create_json_message({
                "code": 500,
                "message": f"Error: {str(e)}",
                "markdown": ""
            })