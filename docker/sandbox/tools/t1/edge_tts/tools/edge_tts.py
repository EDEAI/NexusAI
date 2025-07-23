import uuid
from collections.abc import Generator
from typing import Any

import azure.cognitiveservices.speech as speechsdk
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class EdgeTtsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            speech_key = self.runtime.credentials["speech_key"]
        except KeyError:
            raise Exception("speech_key is not configured or invalid.")

        try:
            service_region = self.runtime.credentials["service_region"]
        except KeyError:
            raise Exception("service_region is not configured or invalid.")

        voice_name = tool_parameters.get("voice_name")
        text = tool_parameters.get("text")

        if not voice_name:
            raise Exception("The voice name cannot be empty")

        if not text:
            raise Exception("The text content cannot be empty.")

        try:
            voice_path = tts(speech_key, service_region, text, voice_name)
            with open(voice_path, "rb") as f:
                audio_bytes = f.read()
            yield self.create_blob_message(audio_bytes, meta = {"mime_type": "audio/wav", "filename": voice_path})
        except Exception as e:
            raise Exception(f"Calling Edge TTS failed: {e}")


def tts(speech_key: str, service_region: str, text: str, voice_name: str = 'zh-CN-XiaohanNeural') -> str | None:
    speech_config = speechsdk.SpeechConfig(subscription = speech_key, region = service_region)
    speech_config.speech_synthesis_voice_name = voice_name

    # Specify the path to output audio file
    audio_filename = uuid.uuid4().__str__() + ".wav"
    audio_config = speechsdk.audio.AudioOutputConfig(filename = audio_filename)

    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config = speech_config, audio_config = audio_config)

    result = speech_synthesizer.speak_text_async(text).get()

    # check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Voice synthesis was successful, and the audio has been saved to:{audio_filename}")
        return audio_filename
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Voice synthesis was cancelled：{cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Voice Error details：{cancellation_details.error_details}")
    return None
