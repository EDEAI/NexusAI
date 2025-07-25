from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base import MiniMaxBaseTool


class MiniMaxMusicGenerationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        group_id = self.runtime.credentials.get("group_id")
        minimax = MiniMaxBaseTool(api_key=api_key, group_id=group_id)

        model = tool_parameters.get("model")
        song_file = tool_parameters.get("song")
        refer_vocal = tool_parameters.get("refer_vocal")
        lyrics = tool_parameters.get("lyrics")

        upload_response = minimax.music_upload(
            file_name=song_file.filename,
            file_blob=song_file.blob,
            mime_type=song_file.mime_type,
        )
        if upload_response.status_code != 200:
            yield self.create_text_message(
                f"Music generation upload failed {upload_response.status_code} {upload_response.text}"
            )
            return
        upload_data = upload_response.json()
        voice_id = upload_data.get("voice_id")
        instrumental_id = upload_data.get("instrumental_id")
        if not voice_id or not instrumental_id:
            yield self.create_text_message(
                f"Music generation upload failed {upload_response.text}"
            )
            return
        gen_response = minimax.music_generation(
            model=model,
            refer_voice=voice_id,
            refer_instrumental=instrumental_id,
            refer_vocal=None if not refer_vocal else refer_vocal,
            lyrics=lyrics,
        )
        if gen_response.status_code != 200:
            yield self.create_text_message(
                f"Music generation failed {gen_response.status_code} {gen_response.text}"
            )
            return
        status_code = gen_response.json().get("base_resp", {}).get("status_code", -1)
        if status_code != 0:
            yield self.create_text_message(
                f"Music generation failed {gen_response.text}"
            )
            return
        audio_hex = gen_response.json().get("data", {}).get("audio")

        if not audio_hex:
            yield self.create_text_message(
                f"Music generation failed {gen_response.text}"
            )
            return
        (self.create_text_message("Audio generated successfully"),)
        yield self.create_blob_message(
            blob=bytes.fromhex(audio_hex), meta={"mime_type": "audio/mpeg"}
        )
