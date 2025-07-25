import json
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.aippt_api import AipptApi, grant_token, AipptApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

class GenerateOutlineTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        api_key, token = self.get_headers_param()
        self.AipptApi = AipptApi(api_key, token)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:

        def output_outline(item):
            return self.create_stream_variable_message("outline", item)

        try:
            # files_req = []
            # for file in tool_parameters.get("files"):
            #     files_req.append(('files', (file.filename, file.blob, file.mime_type)))

            # 创建任务
            task = self.AipptApi.create_task(tool_parameters['title'], tool_parameters['page'], tool_parameters['group'],tool_parameters['scene'], tool_parameters['tone'])

            task_id = task['data']['id']
            yield self.create_variable_message("task_id", task_id)

            # 生成大纲
            outline = self.AipptApi.generate_outline(task_id, output_outline)
            for message in outline:
                yield message

            yield self.create_stream_variable_message("outline", "\n")
        except AipptApiException as e:
            if e.code == 43103: # token invalid，clear api_key，token reset get
                self.session.storage.delete('api_key')
                self.session.storage.delete('token')
            raise ToolProviderCredentialValidationError(str(e))
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
        except json.JSONDecodeError as e:
            raise ToolProviderCredentialValidationError(str(e))

    def get_headers_param(self):
        try:
            api_key = self.session.storage.get('api_key').decode('utf-8')
            token = self.session.storage.get('token').decode('utf-8')

            return api_key, token
        except Exception as e:
            data = grant_token(self.runtime.credentials['api_key'], self.runtime.credentials['secret_key'])

            api_key:str = data['data']['api_key']
            token:str = data['data']['token']

            self.session.storage.set('api_key', api_key.encode('utf-8'))
            self.session.storage.set('token', token.encode('utf-8'))

            return api_key, token