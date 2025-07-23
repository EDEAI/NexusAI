import os
from typing import Any, Generator
import fal_client
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from dify_plugin.file.file import File


class WizperTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        audio_file: File | None = tool_parameters.get("audio_file")
        if not audio_file:
            yield self.create_text_message("No audio file provided")
            return
        
        task = tool_parameters.get("task", "transcribe")
        language = tool_parameters.get("language", "en")
        chunk_level = tool_parameters.get("chunk_level", "segment")
        version = tool_parameters.get("version", "3")

        api_key = self.runtime.credentials["fal_api_key"]
        os.environ["FAL_KEY"] = api_key
        audio_binary = audio_file.blob
        mime_type = audio_file.mime_type
        file_data = audio_binary
        try:
            audio_url = fal_client.upload(file_data, mime_type or "audio/mpeg")
        except Exception as e:
            yield self.create_text_message(f"Error uploading audio file: {str(e)}")
        arguments = {
            "audio_url": audio_url,
            "task": task,
            "language": language,
            "chunk_level": chunk_level,
            "version": version,
        }
        result = fal_client.subscribe("fal-ai/wizper", arguments=arguments, with_logs=False)
        json_message = self.create_json_message(result)
        text = result.get("text", "")
        text_message = self.create_text_message(text)
        yield from [json_message, text_message]