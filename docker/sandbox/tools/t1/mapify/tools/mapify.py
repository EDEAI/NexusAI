import os
import re
import requests
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

MAPIFY_API_URL = 'https://mapify.so/api/v1/preview-mind-maps'

YOUTUBE_REGEX = re.compile(r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/')
WEB_URL_REGEX = re.compile(r'https?://')

class MapifyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        prompt_or_url = tool_parameters.get('prompt-url', '').strip()
        mode = tool_parameters.get('mode', 'prompt')
        language = tool_parameters.get('language', 'en')

        if not prompt_or_url:
            yield self.create_json_message({
                'error': 'Prompt is required.'
            })
            return

        # Determine content type based on model and prompt
        if mode == 'youtube':
            if not YOUTUBE_REGEX.search(prompt_or_url):    
                yield self.create_json_message({
                    'error': 'Invalid YouTube URL.'
                })
                return
        elif mode == 'website':
            if not WEB_URL_REGEX.match(prompt_or_url):
                yield self.create_json_message({    
                    'error': 'Invalid website URL.'
                })
                return
        

        # Prepare the request payload
        payload = {
            'prompt': prompt_or_url,
            'language': language,
            'mode': mode,
            'from': 'dify'
        }

        headers = {
            'Authorization': f'Bearer {self.runtime.credentials["api_key"]}',
            'Content-Type': 'application/json'
        }

        try:
            resp = requests.post(MAPIFY_API_URL, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # Expecting keys: image_url, edit_url, id, etc.
            result = {
                'image_url': data.get('image_url'),
                'edit_url': data.get('edit_url'),
                'id': data.get('id'),
                'meta': data.get('meta', {}),
                'raw': data
            }
            yield self.create_json_message(result)

        except requests.exceptions.RequestException as e:
            yield self.create_json_message({
                'error': f'Failed to generate mind map: {str(e)}'
            })
        except Exception as e:
            yield self.create_json_message({
                'error': f'Unexpected error: {str(e)}'
            })
