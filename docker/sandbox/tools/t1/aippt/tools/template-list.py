from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.core.runtime import Session
from dify_plugin.entities.tool import ToolInvokeMessage, ToolRuntime
from services.aippt_api import AipptApi, grant_token, AipptApiException
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class TemplateListTool(Tool):
    def __init__(self, runtime: ToolRuntime, session: Session):
        super().__init__(runtime, session)
        api_key, token = self.get_headers_param()
        self.AipptApi = AipptApi(api_key, token)


    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            template = self.AipptApi.template_component(tool_parameters['page'], tool_parameters['page_size'], tool_parameters['suit_scene'], tool_parameters['suit_style'], tool_parameters['colour'])
            resp = template['data']

            yield self.create_json_message(resp)

        except AipptApiException as e:
            if e.code == 43103: # token invalid，clear api_key，token reset get
                self.session.storage.delete('api_key')
                self.session.storage.delete('token')
            raise ToolProviderCredentialValidationError(str(e))
        except Exception as e:
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