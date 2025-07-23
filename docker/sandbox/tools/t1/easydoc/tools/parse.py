import logging
import os
import time
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import requests
from dify_plugin.invocations.file import UploadFileResponse
from requests import post,get
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from yarl import URL

logger = logging.getLogger(__name__)





@dataclass
class Credentials:
    base_url: str
    api_key: str
    verify_ssl: bool = True

@dataclass
class ZipContent:
    md_content: str = ""
    content_list: List[Dict[str, Any]] = None
    images: List[UploadFileResponse] = None
    html_content: Optional[str] = None
    docx_content: Optional[bytes] = None
    latex_content: Optional[str] = None

    def __post_init__(self):
        if self.content_list is None:
            self.content_list = []
        if self.images is None:
            self.images = []


class EasyDocTool(Tool):

    def validate_token(self) -> None:
        """Validate URL and token."""
        credentials = self._get_credentials()


        header = self._get_headers(credentials)
        print(f"credentials: {credentials}")
        task_url = self._build_api_url(credentials.base_url, "modes")
        response = requests.get(task_url, headers=header)
      
        if response.status_code != 200:
            logger.error('apply upload url failed. status:{} ,result:{}'.format(response.status_code, response.text))
            raise Exception('apply upload url failed. status:{} ,result:{}'.format(response.status_code, response.text))
        result = response.json()

        if result["success"] != True:
            logger.error('validate token failed, reason:{}'.format(result.get("err_message")))
            raise Exception('validate token failed, reason:{}'.format(result.get("err_message")))



      

    def _get_credentials(self) -> Credentials:
        """Get and validate credentials."""
        base_url = self.runtime.credentials.get("base_url")
        api_key = self.runtime.credentials.get("api_key")
        verify_ssl_value = self.runtime.credentials.get("verify_ssl", True)
        if isinstance(verify_ssl_value, str):
            verify_ssl = verify_ssl_value.lower() in ("true", "1", "yes", "on")
        else:
            verify_ssl = bool(verify_ssl_value)
        if not base_url:
            logger.error("Missing base_url in credentials")
            raise ToolProviderCredentialValidationError("Please input base_url")
        
        return Credentials(base_url=base_url, api_key=api_key, verify_ssl=verify_ssl)


    @staticmethod
    def _get_headers(credentials:Credentials) -> Dict[str, str]:
        """Get request headers."""
        return {
                'api-key': f'{credentials.api_key}',
            }


    @staticmethod
    def _build_api_url(base_url: str, *paths: str) -> str:
        return str(URL(base_url) / "/".join(paths))


    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        credentials = self._get_credentials()
        yield from self.parser_file(credentials, tool_parameters)


    def validate_api_key(self) -> None:
        """Validate URL and token."""
        credentials = self._get_credentials()
        # todo: validate api key
        url = self._build_api_url(credentials.base_url, "api/v4/file-urls/batch")
        logger.info(f"Validating remote server connection to {url}")
        response = post(
                url,
                headers=self._get_headers(credentials),
                timeout=10,
                verify=credentials.verify_ssl,
            )
        if response.status_code!= 200:
            logger.error(f"Remote server validation failed with status {response.status_code}")
            raise ToolProviderCredentialValidationError("Please check your base_url and api_key")


    def _parser_file_remote(self, credentials: Credentials, tool_parameters: Dict[str, Any]):
        """Parse files by remote server."""
        file = tool_parameters.get("file")
        if not file:
            logger.error("No file provided for file parsing")
            raise ValueError("File is required")
        self._validate_file_type(file.filename)

        header = self._get_headers(credentials)
        # create parsing task
        data = {
            "mode": tool_parameters.get("parse_mode", "lite"),
        }
        task_url = self._build_api_url(credentials.base_url, "parse")
        files = {
            "files": (file.filename, file.blob, "application/form-data")
        }
        response = requests.post(task_url, headers=header, files=files, data=data)

      
        if response.status_code != 200:
            logger.error('apply upload url failed. status:{} ,result:{}'.format(response.status_code, response.text))
            raise Exception('apply upload url failed. status:{} ,result:{}'.format(response.status_code, response.text))

        result = response.json()
        if result["success"] == True:
            logger.info('apply upload url success,result:{}'.format(result))
            task_id = result["data"]["task_id"]
            
            extract_result = self._poll_get_parse_result(credentials, task_id)
            if "blocks" in extract_result:
                yield self.create_json_message({"blocks": extract_result["blocks"]})
            if "nodes" in extract_result:
                yield self.create_json_message({"nodes":extract_result["nodes"]})
            if "markdown" in extract_result and extract_result["markdown"]:
                yield self.create_text_message( extract_result["markdown"])
           
        else:
            logger.error('apply upload url failed,reason:{}'.format(result.get("err_message")))
            raise Exception('apply upload url failed,reason:{}'.format(result.get("err_message")))


    def _poll_get_parse_result(self, credentials: Credentials, task_id: str) -> Dict[str, Any]:
        """poll get parser result."""
        url = self._build_api_url(credentials.base_url, f"parse/{task_id}")
        headers = self._get_headers(credentials)
        max_retries = 50
        retry_interval = 5

        for _ in range(max_retries):
            response = get(url, headers=headers, verify=credentials.verify_ssl)
            if response.status_code == 200:
                if response.json().get("success") == True:
                    data = response.json().get("data", {})
                    if data.get("status", "") == "SUCCESS":
                        result = data.get("results", {})[0]    
                        return result   
                    elif data.get("status", "") == "FAILED":
                        logger.error(f"Parse failed, reason: {data.get('msg')}")
                        raise Exception(f"Parse failed, reason: {data.get('msg')}")
                    else:
                        logger.info(f"Parse in progress, state: {data.get('status')}")
                        time.sleep(retry_interval)
                        continue
                else:
                    logger.error(f"Parse failed, reason: {response.json().get('msg')}")
                    raise Exception(f"Parse failed, reason: {response.json().get('msg')}")
            else:
                logger.warning(f"Failed to get parse result, status: {response.status_code}")
                raise Exception(f"Failed to get parse result, status: {response.status_code}")

            time.sleep(retry_interval)

        logger.error("Polling timeout reached without getting completed result")
        raise TimeoutError("Parse operation timed out")



    @staticmethod
    def _validate_file_type(filename: str) -> str:
        extension = os.path.splitext(filename)[1].lower()
        if extension not in [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".png", ".jpg", ".jpeg"]:
            raise ValueError(f"File extension {extension} is not supported")
        return extension


    def parser_file(
        self,
        credentials: Credentials,
        tool_parameters: Dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        
        yield from self._parser_file_remote(credentials, tool_parameters)

