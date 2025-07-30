from collections.abc import Generator
from typing import Any
import tempfile
import os
import subprocess
import json


from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class CompressAudioTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        audio_file: File = tool_parameters["audio_file"]

        if audio_file.type != "audio":
            raise ValueError("The file is not an audio, file type: " + audio_file.type)

        bitrate = tool_parameters.get("bitrate", "16k")
        sample_rate = tool_parameters.get("sample_rate", "8000")
        compression_level = str(tool_parameters.get("compression_level", 4))

        compressed_bytes, info = compress_audio(
            audio_file.blob,
            audio_file.extension,
            bitrate,
            sample_rate,
            compression_level,
        )

        yield self.create_json_message(info)
        yield self.create_blob_message(
            blob=compressed_bytes, meta={"mime_type": audio_file.mime_type}
        )


AUDIO_CODEC_MAP = {
    ".mp3": "libmp3lame",
    ".aac": "aac",
    ".m4a": "aac",
    ".ogg": "libvorbis",
    ".wav": None,
    ".wma": "wmav2",
    ".flac": "flac",
}


def compress_audio(
    input_bytes,
    output_format="mp3",
    bitrate="32k",
    sample_rate="8000",
    compression_level="4",
):
    with tempfile.NamedTemporaryFile(
        suffix=f".{output_format}", delete=False
    ) as temp_in, tempfile.NamedTemporaryFile(
        suffix=f".{output_format}", delete=False
    ) as temp_out:
        try:
            temp_in.write(input_bytes)
            temp_in.flush()

            probe_cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                temp_in.name
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            audio_info = json.loads(probe_result.stdout)
            
            duration = float(audio_info["format"]["duration"])
            codec = AUDIO_CODEC_MAP.get(output_format)
            if not codec:
                codec = "copy" 
            
            compress_cmd = [
                "ffmpeg",
                "-i", temp_in.name,
                "-c:a", codec,
                "-b:a", bitrate,      # 设置比特率
                "-ac", "1",           # 转换为单声道
                "-ar", sample_rate,   # 设置采样率
                "-compression_level", compression_level,  # 压缩级别
                "-y",                 # 覆盖输出文件
                temp_out.name
            ]
            
            subprocess.run(compress_cmd, check=True)

            with open(temp_out.name, "rb") as f:
                compressed_bytes = f.read()

            original_size_mb = len(input_bytes) / (1024 * 1024)
            compressed_size_mb = len(compressed_bytes) / (1024 * 1024)

            info = {
                "original_size": f"{round(original_size_mb, 2)} MB",
                "compressed_size": f"{round(compressed_size_mb, 2)} MB",
                "compression_ratio": f"{round(compressed_size_mb / original_size_mb * 100, 2)}%",
                "duration": f"{round(duration, 2)}s",
                "format": output_format,
                "codec": codec,
                "sample_rate": f"{sample_rate}Hz",
                "channels": "1",
            }

            return compressed_bytes, info

        finally:
            for temp_file in [temp_in.name, temp_out.name]:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
