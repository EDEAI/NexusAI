from collections.abc import Generator
from typing import Any
import tempfile
import os
import time
import ffmpeg

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class ExtractAudioTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        video_file = tool_parameters.get('video')
        audio_format = tool_parameters.get('audio_format', 'mp3').lower()
        
        # 验证输入
        if not video_file:
            yield self.create_text_message("No video file provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No video file provided"
            })
            return
        
        # 验证音频格式
        valid_formats = ['mp3', 'aac', 'wav', 'ogg', 'flac']
        if audio_format not in valid_formats:
            yield self.create_text_message(f"Invalid audio format: {audio_format}. Using 'mp3' instead.")
            audio_format = 'mp3'
        
        try:
            # 设置临时文件
            video_file_extension = video_file.extension if video_file.extension else '.mp4'
            
            # 获取原始文件名（不带扩展名）
            orig_filename = os.path.splitext(video_file.filename)[0]
            output_filename = f"{orig_filename}.{audio_format}"
            
            # 设置MIME类型映射
            mime_types = {
                'mp3': 'audio/mpeg',
                'aac': 'audio/aac',
                'wav': 'audio/wav',
                'ogg': 'audio/ogg',
                'flac': 'audio/flac'
            }
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=video_file_extension) as in_temp_file:
                in_temp_file.write(video_file.blob)
                in_temp_path = in_temp_file.name
                
            out_temp_path = os.path.join(tempfile.gettempdir(), f"audio_{int(time.time())}.{audio_format}")
            
            try:
                # 执行提取
                yield self.create_text_message(f"Extracting audio from video to {audio_format} format...")
                
                # 使用ffmpeg-python库提取音频
                (
                    ffmpeg
                    .input(in_temp_path)
                    .output(out_temp_path, acodec=self._get_codec_for_format(audio_format))
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                
                # 读取输出文件
                with open(out_temp_path, 'rb') as out_file:
                    audio_data = out_file.read()
                
                # 计算音频文件大小
                audio_size = os.path.getsize(out_temp_path)
                
                # 创建结果消息
                yield self.create_blob_message(
                    audio_data,
                    meta={
                        "filename": output_filename,
                        "mime_type": mime_types.get(audio_format, f"audio/{audio_format}"),
                    }
                )
                
                yield self.create_json_message({
                    "status": "success",
                    "message": f"Successfully extracted audio from video to {audio_format} format",
                    "original_filename": video_file.filename,
                    "audio_filename": output_filename,
                    "audio_format": audio_format,
                    "audio_size": audio_size
                })
                
                # 生成人类可读的摘要
                summary = f"Successfully extracted audio from {video_file.filename}\n\n"
                summary += f"Audio Format: {audio_format}\n"
                summary += f"Output File: {output_filename}\n"
                summary += f"Audio Size: {audio_size / (1024*1024):.2f} MB"
                
                yield self.create_text_message(summary)
                
            finally:
                # 清理临时文件
                if os.path.exists(in_temp_path):
                    os.unlink(in_temp_path)
                if os.path.exists(out_temp_path):
                    os.unlink(out_temp_path)
                    
        except Exception as e:
            error_msg = f"Error extracting audio: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "status": "error",
                "message": error_msg
            })
    
    def _get_codec_for_format(self, audio_format):
        """根据音频格式返回适当的编解码器"""
        codecs = {
            'mp3': 'libmp3lame',
            'aac': 'aac',
            'wav': 'pcm_s16le',
            'ogg': 'libvorbis',
            'flac': 'flac'
        }
        return codecs.get(audio_format, 'copy') 