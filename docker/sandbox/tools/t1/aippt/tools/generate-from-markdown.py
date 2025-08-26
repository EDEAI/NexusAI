import json
import time
import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.aippt_api import AipptApi, grant_token, AipptApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class GenerateFromMarkdownTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        api_key, token = self.get_headers_param()
        self.AipptApi = AipptApi(api_key, token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            # Step 1: Create task with type=7 for markdown content
            task = self.AipptApi.create_task(
                title=tool_parameters['title'],
                content=tool_parameters['content'],
                task_type=7
            )
            task_id = task['data']['id']
            
            # Step 2: Generate design using selected template
            design = self.AipptApi.design_save(task_id, int(tool_parameters['template_id']))
            design_id = design['data']['id']
            
            # Step 3: Export design
            export_result = self.AipptApi.design_export(design_id)
            task_key = export_result['data']
            
            # Step 4: Poll for export result (max 1 hour = 3600 seconds)
            while True:
                result = self.AipptApi.design_export_result(task_key)
                if result['msg'] == '导出中':
                    pass
                elif result['msg'] == '导出成功':
                    break

                time.sleep(3)

            url = result['data'][0]
            response = requests.get(url)
            response.raise_for_status()
            yield self.create_blob_message(blob=response.content, meta={"mime_type": response.headers.get('Content-Type')})
            # yield self.create_text_message(url)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))

    def get_headers_param(self):
        # Get token directly from grant_token function without using session storage
        data = grant_token(self.runtime.credentials['api_key'], self.runtime.credentials['secret_key'])
        
        if data['code'] != 0:
            raise ToolProviderCredentialValidationError(f"Failed to get token: {data['msg']}")
        
        api_key: str = data['data']['api_key']
        token: str = data['data']['token']
        
        return api_key, token