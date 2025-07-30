from collections.abc import Generator
from typing import Any
import requests
import json
import tempfile
import pathlib

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class OpenaiAudioTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        
        if not api_key:
            raise Exception("API key not found in credentials")
        
        file_data = tool_parameters.get("file")
        transcription_type = tool_parameters.get("transcription_type", "transcribe")
        model = tool_parameters.get("model", "gpt-4o-transcribe")
        response_format = tool_parameters.get("response_format", "text")
        prompt = tool_parameters.get("prompt", "")
        language = tool_parameters.get("language", "")
        timestamp_granularities = tool_parameters.get("timestamp_granularities", "none")
        stream = tool_parameters.get("stream", False)
        output_format = tool_parameters.get("output_format", "default")
        
        if transcription_type == "translate":
            if model != "whisper-1":
                model = "whisper-1"
            api_endpoint = "https://api.openai.com/v1/audio/translations"
        else:
            api_endpoint = "https://api.openai.com/v1/audio/transcriptions"
        
        if model != "whisper-1" and response_format in ["verbose_json", "srt", "vtt"]:
            response_format = "text"
            
        if model != "whisper-1" and timestamp_granularities != "none":
            timestamp_granularities = "none"
        
        if stream and not model.startswith("gpt-4o"):
            stream = False
        
        if not file_data:
            raise Exception("No audio file provided")
            
        try:
            if isinstance(file_data, dict):
                file_content = file_data.get("content")
                file_name = file_data.get("name", "audio_file")
                file_type = file_data.get("type", "")
            elif hasattr(file_data, "read"):
                file_content = file_data.read()
                file_name = getattr(file_data, "name", "audio_file")
                file_type = ""
            elif str(type(file_data)).find("dify_plugin.file.file.File") >= 0:
                original_filename = ""
                file_extension = ""
                
                if hasattr(file_data, "filename") and file_data.filename:
                    original_filename = file_data.filename
                    
                if hasattr(file_data, "extension") and file_data.extension:
                    file_extension = file_data.extension
                    
                if hasattr(file_data, "url"):
                    try:
                        file_response = requests.get(file_data.url)
                        if file_response.status_code == 200:
                            file_content = file_response.content
                        else:
                            raise Exception(f"Failed to download file from URL: {file_response.status_code}")
                    except Exception as download_error:
                        raise Exception(f"Error downloading file from URL: {str(download_error)}")
                elif hasattr(file_data, "content"):
                    file_content = file_data.content
                elif hasattr(file_data, "read") and callable(file_data.read):
                    file_content = file_data.read()
                else:
                    raise Exception("Dify File object does not have accessible content")
                
                if original_filename:
                    file_name = original_filename
                elif file_extension:
                    file_name = f"audio_file{file_extension}"
                else:
                    file_name = "audio_file.mp4"
                
                if hasattr(file_data, "type"):
                    file_type = file_data.type
                elif hasattr(file_data, "mime_type"):
                    file_type = file_data.mime_type
                else:
                    file_type = ""
            else:
                raise Exception(f"Unsupported file data type: {type(file_data)}")
            
            if not file_content:
                raise Exception("Empty file content")
                
            file_ext = ".mp4"
            if file_name and '.' in file_name:
                file_ext = file_name[file_name.rindex('.'):]  # Get everything after the last dot
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                temp_file.write(file_content.encode() if isinstance(file_content, str) else file_content)
                temp_file_path = temp_file.name
            
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            request_data = {
                "model": model,
                "response_format": response_format
            }
            
            if prompt:
                request_data["prompt"] = prompt
                
            if language:
                request_data["language"] = language
                
            if timestamp_granularities != "none" and model == "whisper-1":
                request_data["response_format"] = "verbose_json"
                if timestamp_granularities == "segment":
                    request_data["timestamp_granularities"] = ["segment"]
                elif timestamp_granularities == "word":
                    request_data["timestamp_granularities"] = ["word"]
                elif timestamp_granularities == "segment_and_word":
                    request_data["timestamp_granularities"] = ["segment", "word"]
            
            if stream:
                request_data["stream"] = True
            
            files = {
                "file": (file_name, open(temp_file_path, "rb"), file_type)
            }
            
            if stream:
                with requests.post(
                    api_endpoint,
                    headers=headers,
                    data=request_data,
                    files=files,
                    stream=True
                ) as response:
                    if response.status_code != 200:
                        raise Exception(f"Error {response.status_code}: {response.text}")
                    
                    buffer = ""
                    for line in response.iter_lines():
                        if line:
                            line_text = line.decode('utf-8')
                            
                            if line_text.startswith('data: '):
                                data = line_text[6:]
                                if data == "[DONE]":
                                    break
                                    
                                try:
                                    json_data = json.loads(data)
                                    
                                    if 'type' in json_data and json_data['type'] == 'transcript.text.delta':
                                        if 'delta' in json_data:
                                            text_chunk = json_data['delta']
                                            buffer += text_chunk
                                            yield self.create_text_message(text_chunk)
                                    
                                    elif 'type' in json_data and json_data['type'] == 'transcript.text.done':
                                        if 'text' in json_data:
                                            buffer = json_data['text']
                                            yield self.create_text_message(buffer)
                                    
                                    elif 'choices' in json_data and len(json_data['choices']) > 0:
                                        delta = json_data['choices'][0].get('delta', {})
                                        if 'text' in delta:
                                            text_chunk = delta['text']
                                            buffer += text_chunk
                                            yield self.create_text_message(text_chunk)
                                except json.JSONDecodeError:
                                    pass
                    
                    if buffer and output_format in ["default", "json_only"]:
                        yield self.create_json_message({"result": {"text": buffer}})
            else:
                response = requests.post(
                    api_endpoint,
                    headers=headers,
                    data=request_data,
                    files=files
                )
                
                if response.status_code != 200:
                    raise Exception(f"Error {response.status_code}: {response.text}")
                    
                if response_format in ["json", "verbose_json"]:
                    result = response.json()
                else:
                    result = {"text": response.text}
                
                if output_format == "json_only":
                    yield self.create_json_message({"result": result})
                elif output_format == "text_only":
                    if isinstance(result, dict) and "text" in result:
                        yield self.create_text_message(result["text"])
                    else:
                        yield self.create_text_message(str(result))
                else:
                    yield self.create_json_message({"result": result})
                    
                    if isinstance(result, dict) and "text" in result:
                        yield self.create_text_message(result["text"])
                    else:
                        yield self.create_text_message(str(result))
            
            try:
                pathlib.Path(temp_file_path).unlink()
            except Exception:
                pass
            
        except Exception as e:
            raise Exception(f"Exception while processing audio: {str(e)}")
