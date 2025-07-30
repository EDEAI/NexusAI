import uuid
from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from tools.base import MiniMaxBaseTool


class MiniMaxVoiceCloneTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("api_key")
        group_id = self.runtime.credentials.get("group_id")
        minimax = MiniMaxBaseTool(api_key=api_key, group_id=group_id)

        model = tool_parameters.get("model")
        ref_voice = tool_parameters.get("ref_voice")
        voice_id = tool_parameters.get("voice_id")
        if not voice_id:
            voice_id = f"voice_{uuid.uuid4()}"
        text = tool_parameters.get("text")
        accuracy = tool_parameters.get("accuracy", 0.7)
        need_noise_reduction = tool_parameters.get("need_noise_reduction", False)
        need_volume_normalization = tool_parameters.get(
            "need_volume_normalization", False
        )

        upload_response = minimax.file_upload(
            file_name=ref_voice.filename,
            file_blob=ref_voice.blob,
            mime_type=ref_voice.mime_type,
            purpose="voice_clone",
        )
        if upload_response.status_code != 200:
            yield self.create_text_message(
                f"Voice clone upload failed {upload_response.status_code} {upload_response.text}"
            )
            return
        upload_data = upload_response.json().get("file", {})
        file_id = upload_data.get("file_id")
        if not file_id:
            yield self.create_text_message(
                f"Voice clone upload failed {upload_response.text}"
            )
            return
        clone_response = minimax.voice_clone(
            model=model,
            file_id=file_id,
            voice_id=voice_id,
            text=text,
            accuracy=accuracy,
            need_noise_reduction=need_noise_reduction,
            need_volume_normalization=need_volume_normalization,
        )
        if clone_response.status_code != 200:
            yield self.create_text_message(
                f"Voice clone failed {clone_response.status_code} {clone_response.text}"
            )
            return
        status_code = clone_response.json().get("base_resp", {}).get("status_code", -1)
        if status_code != 0:
            yield self.create_text_message(f"Voice clone failed {clone_response.text}")
            return

        demo_audio = clone_response.json().get("demo_audio")

        if demo_audio:
            yield self.create_text_message(demo_audio)

            # response = requests.get(demo_audio, timeout=60)
            # response.raise_for_status()
            # yield self.create_blob_message(
            #     blob=response.content, meta={"mime_type": "audio/mpeg"}
            # )

        voice_clone_data = {"voice_id": voice_id, "demo_audio": demo_audio}
        yield self.create_json_message(voice_clone_data)
