from collections.abc import Generator
from typing import Any
import tempfile
import os
import subprocess
import json

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class CompressVideoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        video_file: File = tool_parameters["video_file"]

        if video_file.type != "video":
            raise ValueError("The file is not an video, file type: " + video_file.type)

        target_height = int(tool_parameters.get("target_height", 720))
        fps = int(tool_parameters.get("fps", 1))
        crf = str(tool_parameters.get("crf", 35))
        preset = tool_parameters.get("preset", "slower")

        compressed_bytes, info = compress_video(
            input_bytes=video_file.blob,
            output_format=video_file.extension,
            target_height=target_height,
            fps=fps,
            crf=crf,
            preset=preset,
        )

        yield self.create_json_message(info)
        yield self.create_blob_message(
            blob=compressed_bytes, meta={"mime_type": video_file.mime_type}
        )


def compress_video(
    input_bytes: bytes,
    output_format: str = "mp4",
    target_height: int = 720,
    fps: int = 1,
    crf: str = "35",
    preset: str = "slower",
):
    with tempfile.NamedTemporaryFile(
        suffix=f".{output_format}", delete=False
    ) as temp_in, tempfile.NamedTemporaryFile(
        suffix=f".{output_format}", delete=False
    ) as temp_out:
        try:
            temp_in.write(input_bytes)
            temp_in.flush()

            # 获取视频信息
            probe_cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                temp_in.name
            ]
            probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
            video_info = json.loads(probe_result.stdout)
            
            # 获取原始视频尺寸
            video_stream = next(s for s in video_info["streams"] if s["codec_type"] == "video")
            original_width = int(video_stream["width"])
            original_height = int(video_stream["height"])
            original_duration = float(video_info["format"]["duration"])
            
            # 计算新的尺寸
            if original_height > target_height:
                new_height = target_height
                new_width = int(original_width * target_height / original_height)
                size_filter = f"scale={new_width}:{new_height}"
            else:
                new_width = original_width
                new_height = original_height
                size_filter = "copy"

            # 压缩视频
            compress_cmd = [
                "ffmpeg",
                "-i", temp_in.name,
                "-c:v", "libx264",
                "-preset", preset,
                "-crf", crf,
                "-maxrate", "1.5M",
                "-bufsize", "2M",
                "-movflags", "+faststart",
                "-profile:v", "baseline",
                "-vf", size_filter,
                "-r", str(fps),
                "-c:a", "aac",
                "-b:a", "8k",
                "-y",
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
                "resolution": f"{original_width}x{original_height} -> {new_width}x{new_height}",
                "duration": f"{round(original_duration, 2)}s",
            }

            return compressed_bytes, info

        finally:
            for temp_file in [temp_in.name, temp_out.name]:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
