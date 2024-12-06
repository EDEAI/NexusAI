import json
import re

from datetime import date
from pathlib import Path
from mimetypes import guess_extension
from random import choices
from string import ascii_lowercase, digits
from time import monotonic
from typing import Any, Dict, Optional, Union
from urllib.parse import unquote

import httpx

from httpx import Headers, Response, URL

from . import Node
from ..context import Context, replace_variable_value_with_context
from ..variables import ObjectVariable, Variable, VariableTypes, validate_required_variable
from config import settings
from languages import get_language_content
from log import Logger


logger = Logger.get_logger('celery-app')
project_root = Path(__file__).absolute().parent.parent.parent.parent

class HttpRequestNode(Node):
    """
    A HttpRequestNode object is used to make HTTP requests to external APIs.
    """
    
    def __init__(
        self,
        title,
        desc: str = "",
        input: Optional[ObjectVariable] = None,
        wait_for_all_predecessors: bool = False,
        manual_confirmation: bool = False,
        flow_data: Dict[str, Any] = {},
        original_node_id: Optional[str] = None
    ):
        """
        Initializes a HttpRequestNode object.
        """
        init_kwargs = {
            "type": "http_request",
            "title": title,
            "desc": desc,
            "input": input,
            "wait_for_all_predecessors": wait_for_all_predecessors,
            "manual_confirmation": manual_confirmation,
            "flow_data": flow_data
        }
        if original_node_id is not None:
            init_kwargs["original_node_id"] = original_node_id
        
        super().__init__(**init_kwargs)
            
    @staticmethod
    def _content_type_is_file(content_type: str) -> bool:
        """
        Checks if the content type is a file.
        """
        if any(
            v in content_type
            for v in [
                'image',
                'audio', 
                'video',
                'zip'
            ]
        ):
            return True
        elif content_type.startswith('application/octet-stream'):
            return True
        return False
    
    @classmethod
    def _generate_file_name(
        cls,
        url: URL,
        content_type: str,
        content_disposition: str
    ) -> str:
        file_name = 'download'
        url_without_args = url.path.split('/')[-1]
        if url_without_args:
            file_name = url_without_args
        if content_type:
            file_suffix = guess_extension(content_type)
            if file_suffix:
                file_name = Path(file_name).with_suffix(file_suffix).name
        if content_disposition:
            match = re.search(r'filename="(.*)"', content_disposition)
            if match:
                file_name = unquote(match[1].replace('\\"', '"'))
                if '/' in file_name:
                    match = re.search(r'.*/(.*?)', file_name)
                    if match and match[1]:
                        file_name = match[1]
        random_str = ''.join(choices(ascii_lowercase + digits, k=8))
        file_path = Path(file_name)
        return file_path.with_stem(f'{file_path.stem}-{random_str}').name
        
    def _generate_request(
        self,
        input_: ObjectVariable
    ) -> Response:
        """
        Generates an HTTP request based on the input data.
        """
        method: str = input_.properties['method'].value
        url: str = input_.properties['url'].value
        headers: Dict[str, str] = {
            key: value.value
            for key, value in input_.properties.get('headers', ObjectVariable(name="default")).properties.items()
        }
        try:
            headers = Headers(headers)
        except UnicodeEncodeError:
            raise Exception('Non-ASCII characters in HTTP headers are not allowed.')
        params: Dict[str, str] = {
            key: value.value
            for key, value in input_.properties.get('params', ObjectVariable(name="default")).properties.items()
        }
        body_type: str = input_.properties.get('body_type', Variable(name="default", type="string", value="none")).value
        body_data_var: Optional[VariableTypes] = input_.properties.get('body_data', None)
        connect_timeout = input_.properties.get('connect_timeout')
        connect_timeout: Union[int, float] = (
            settings.HTTP_CONNECT_TIMEOUT
            if connect_timeout is None else connect_timeout.value
        )
        read_timeout = input_.properties.get('read_timeout')
        read_timeout: Union[int, float] = (
            settings.HTTP_READ_TIMEOUT
            if read_timeout is None else read_timeout.value
        )
        write_timeout = input_.properties.get('write_timeout')
        write_timeout: Union[int, float] = (
            settings.HTTP_WRITE_TIMEOUT
            if write_timeout is None else write_timeout.value
        )
        request_kwargs = {
            'url': url,
            'params': params,
            'headers': headers,
            'timeout': (
                connect_timeout,
                read_timeout,
                write_timeout
            ),
            'follow_redirects': True
        }
        method = method.lower()
        match method:
            case 'get' | 'head' | 'options' | 'delete':
                # These requests should not include a request body.
                return getattr(httpx, method)(**request_kwargs)
            case 'post' | 'put' | 'patch':
                match body_type:
                    case 'none':
                        return getattr(httpx, method)(**request_kwargs)
                    case 'form-data':
                        if body_data_var is None:
                            raise ValueError('body_data is required for form-data body type')
                        # body_data is an ObjectVariable whose properties are string Variables
                        return getattr(httpx, method)(
                            files={
                                key: value.value
                                for key, value in body_data_var.properties.items()
                            },
                            **request_kwargs
                        )
                    case 'x-www-form-urlencoded':
                        if body_data_var is None:
                            raise ValueError('body_data is required for x-www-form-urlencoded body type')
                        # body_data is an ObjectVariable whose properties are string Variables
                        return getattr(httpx, method)(
                            data={
                                key: value.value
                                for key, value in body_data_var.properties.items()
                            },
                            **request_kwargs
                        )
                    case 'raw-text':
                        if body_data_var is None:
                            raise ValueError('body_data is required for raw-text body type')
                        # body_data is a string Variable
                        return getattr(httpx, method)(data=body_data_var.value, **request_kwargs)
                    case 'json':
                        if body_data_var is None:
                            raise ValueError('body_data is required for json body type')
                        # body_data is a string Variable of JSON format
                        try:
                            return getattr(httpx, method)(
                                json=json.loads(body_data_var.value),
                                **request_kwargs
                            )
                        except json.JSONDecodeError:
                            raise ValueError('Invalid JSON format for body data')
                    case _:
                        raise ValueError(f'Invalid body type {self.data["body_type"]}')
            case _:
                raise ValueError(f'Invalid http method {method}')
            
    def _parse_response(self, response: Response) -> Variable:
        """
        Parses the response from an HTTP request.
        """
        # assert response.is_success, f'HTTP request failed with status code {response.status_code}'
        assert response.is_success, get_language_content('http_request_failed').format(status_code=response.status_code)
        response_len = len(response.content)
        content_type = response.headers.get('content-type', '')
        if self._content_type_is_file(content_type):
            # assert response_len <= settings.HTTP_RESPONSE_MAX_BINARY_SIZE, (
            #     f'HTTP response content is too large, max size is {settings.HTTP_RESPONSE_MAX_BINARY_SIZE}, '
            #     f'but current size is {response_len}'
            # )
            assert response_len <= settings.HTTP_RESPONSE_MAX_BINARY_SIZE, (
                get_language_content('http_response_content_oversize').format(
                    max_size=settings.HTTP_RESPONSE_MAX_BINARY_SIZE,
                    size=response_len
                )
            )
            today = date.today()
            today_path = project_root.joinpath(
                'download_files',
                str(today.year),
                str(today.month),
                str(today.day)
            )
            today_path.mkdir(parents=True, exist_ok=True)
            filename = self._generate_file_name(
                response.url,
                content_type,
                response.headers.get('content-disposition', '')
            )
            file_path = today_path.joinpath(filename)
            with file_path.open('wb') as f:
                f.write(response.content)
            return Variable('output', 'file', 'output', str(file_path.relative_to(project_root)))
        else:
            # assert response_len <= settings.HTTP_RESPONSE_MAX_TEXT_SIZE, (
            #     f'HTTP response content is too large, max size is {settings.HTTP_RESPONSE_MAX_TEXT_SIZE}, '
            #     f'but current size is {response_len}'
            # )
            assert response_len <= settings.HTTP_RESPONSE_MAX_BINARY_SIZE, (
                get_language_content('http_response_content_oversize').format(
                    max_size=settings.HTTP_RESPONSE_MAX_TEXT_SIZE,
                    size=response_len
                )
            )
            return Variable('output', 'string', 'output', response.text)
        
    def run(self, context: Context, **kwargs) -> Dict[str, Any]:
        """
        Executes the HTTP request node.
        """
        try:
            start_time = monotonic()
            input_ = self.data['input']
            replace_variable_value_with_context(input_, context)
            validate_required_variable(input_)
            response = self._generate_request(input_)
            outputs = self._parse_response(response)
            return {
                'status': 'success',
                'message': 'HTTP request node executed successfully.',
                'data': {
                    'elapsed_time': monotonic() - start_time,
                    'inputs': input_.to_dict(),
                    'outputs': outputs.to_dict()
                }
            }
        except Exception as e:
            logger.exception('ERROR!!')
            return {
                'status': 'failed',
                'message': str(e)
            }
        