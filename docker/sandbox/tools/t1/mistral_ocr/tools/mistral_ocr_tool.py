import json
from typing import Any, Generator, Optional, Literal
from dify_plugin.file.file import File
import base64
import os
import requests
import io
from pydantic import BaseModel
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
import tempfile


class MistralOCRTool(Tool):
    def _upload_file_api(self, file: File) -> str:
        api_key = self.runtime.credentials.get('mistral_api_key', '')
        
        headers = {
            "Authorization": f"Bearer {api_key}"
        }
        
        filename = file.filename or "uploaded_file"
        if file.extension and not filename.endswith(file.extension):
            filename += file.extension
            
        files = {
            "file": (filename, io.BytesIO(file.blob))
        }
        
        data = {
            "purpose": "ocr"
        }
        
        upload_response = requests.post(
            "https://api.mistral.ai/v1/files",
            headers=headers,
            files=files,
            data=data
        )
        
        if upload_response.status_code != 200:
            raise Exception(f"File upload error: {upload_response.status_code} - {upload_response.text}")
        
        file_id = upload_response.json().get("id")
        
        url_response = requests.get(
            f"https://api.mistral.ai/v1/files/{file_id}/url",
            headers=headers
        )
        
        if url_response.status_code != 200:
            raise Exception(f"Get URL error: {url_response.status_code} - {url_response.text}")
        
        return url_response.json().get("url")

    def _get_document_type(self, file: File) -> Literal["document_url", "image_url"]:
        if file.mime_type is not None:
            if file.mime_type.startswith("image/"):
                return "image_url"
            else:
                return "document_url"
        elif file.extension in [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]:
            return "document_url"
        else:
            return "image_url"

    def _direct_ocr_api_call(self, api_key, document, model="mistral-ocr-latest", pages=None, image_limit=None, image_min_size=None):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        payload = {
            "model": model,
            "document": document
        }
        
        if pages is not None:
            payload["pages"] = pages
        if image_limit is not None:
            payload["image_limit"] = image_limit
        if image_min_size is not None:
            payload["image_min_size"] = image_min_size
            
        response = requests.post(
            "https://api.mistral.ai/v1/ocr",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"OCR API error: {response.status_code} - {response.text}")

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        file_input = tool_parameters.get("file_path", None)
        if not file_input:
            yield self.create_text_message("Please provide a valid file")
            return
        
        pages = None
        pages_param = tool_parameters.get("pages", None)
        if isinstance(pages_param, str) and pages_param.strip():
            try:
                result_pages = []
                for part in pages_param.split(","):
                    part = part.strip()
                    if "-" in part:
                        start, end = map(int, part.split("-"))
                        result_pages.extend(range(start, end + 1))
                    elif part:
                        result_pages.append(int(part))
                pages = result_pages if result_pages else None
            except ValueError:
                pass
        elif isinstance(pages_param, (int, float)):
            pages = [int(pages_param)]
        
        image_limit = tool_parameters.get("image_limit", None)
        image_min_size = tool_parameters.get("image_min_size", None)

        try:
            api_key = self.runtime.credentials.get('mistral_api_key', '')
            
            doc_type = self._get_document_type(file_input)
            document = {
                "type": doc_type
            }
            
            if doc_type == "document_url":
                document["document_url"] = self._upload_file_api(file_input)
            else:
                base64_image = base64.b64encode(file_input.blob).decode("utf-8")
                document["image_url"] = f"data:{file_input.mime_type or 'image/jpeg'};base64,{base64_image}"

            response = self._direct_ocr_api_call(
                api_key=api_key,
                document=document,
                pages=pages,
                image_limit=image_limit,
                image_min_size=image_min_size
            )

            yield self.create_json_message(response)
        except Exception as e:
            yield self.create_text_message(f"Unexpected error in Mistral OCR tool: {str(e)}")
            