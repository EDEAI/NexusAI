import concurrent.futures
import io
import random
import warnings
from typing import Any, Literal, Optional, Union, Generator
import openai
from yarl import URL
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import Tool

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from pydub import AudioSegment


class ToolParameterValidationError(Exception):
    pass


class PodcastAudioGeneratorTool(Tool):
    @staticmethod
    def _generate_silence(duration: float):
        silence = AudioSegment.silent(duration=int(duration * 1000))
        return silence

    @staticmethod
    def _generate_audio_segment(
            client: openai.OpenAI,
            line: str,
            voice: Literal["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
            index: int,
    ) -> tuple[int, Union[AudioSegment, str], Optional[AudioSegment]]:
        try:
            response = client.audio.speech.create(model="tts-1", voice=voice, input=line.strip(), response_format="wav")
            audio = AudioSegment.from_wav(io.BytesIO(response.content))
            silence_duration = random.uniform(0.1, 1.5)
            silence = PodcastAudioGeneratorTool._generate_silence(silence_duration)
            return (index, audio, silence)
        except Exception as e:
            return (index, f"Error generating audio: {str(e)}", None)

    def _invoke(
            self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        script = tool_parameters.get("script", "")
        host1_voice = tool_parameters.get("host1_voice")
        host2_voice = tool_parameters.get("host2_voice")
        script_lines = [line for line in script.split("\n") if line.strip()]
        if not host1_voice or not host2_voice:
            raise ToolParameterValidationError("Host voices are required")
        if not self.runtime or not self.runtime.credentials:
            raise ToolProviderCredentialValidationError("Tool runtime or credentials are missing")
        api_key = self.runtime.credentials.get("api_key")
        if not api_key:
            raise ToolProviderCredentialValidationError("OpenAI API key is missing")
        openai_base_url = self.runtime.credentials.get("openai_base_url", None)
        openai_base_url = str(URL(openai_base_url) / "v1") if openai_base_url else None
        client = openai.OpenAI(api_key=api_key, base_url=openai_base_url)
        max_workers = 5
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, line in enumerate(script_lines):
                voice = host1_voice if i % 2 == 0 else host2_voice
                future = executor.submit(self._generate_audio_segment, client, line, voice, i)
                futures.append(future)
            audio_segments: list[Any] = [None] * len(script_lines)
            for future in concurrent.futures.as_completed(futures):
                (index, audio, silence) = future.result()
                if isinstance(audio, str):
                    yield self.create_text_message(audio)
                audio_segments[index] = (audio, silence)
        combined_audio = AudioSegment.empty()
        for i, (audio, silence) in enumerate(audio_segments):
            if audio:
                combined_audio += audio
                if i < len(audio_segments) - 1 and silence:
                    combined_audio += silence
        buffer = io.BytesIO()
        combined_audio.export(buffer, format="wav")
        wav_bytes = buffer.getvalue()
        for resp in [
            self.create_text_message("Audio generated successfully"),
            self.create_blob_message(blob=wav_bytes, meta={"mime_type": "audio/x-wav"}),
        ]:
            yield resp
