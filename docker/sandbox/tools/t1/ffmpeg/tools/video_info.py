from collections.abc import Generator
from typing import Any
import tempfile
import os
import json
import subprocess

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class VideoInfoTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        video_file = tool_parameters.get('video')
        
        if not video_file:
            yield self.create_text_message("No video file provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No video file provided"
            })
            return
        
        try:
            # 创建临时文件保存上传的视频
            file_extension = video_file.extension if video_file.extension else '.mp4'
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                temp_file.write(video_file.blob)
                temp_file_path = temp_file.name
            
            try:
                # 使用ffprobe获取视频信息
                command = [
                    'ffprobe', 
                    '-v', 'quiet',
                    '-print_format', 'json',
                    '-show_format',
                    '-show_streams',
                    temp_file_path
                ]
                
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                if result.returncode != 0:
                    error_msg = f"Error analyzing video file: {result.stderr}"
                    yield self.create_text_message(error_msg)
                    yield self.create_json_message({
                        "status": "error",
                        "message": error_msg
                    })
                    return
                
                # 解析JSON结果
                info = json.loads(result.stdout)
                
                # 提取关键信息
                formatted_info = {
                    "status": "success",
                    "filename": video_file.filename,
                    "format": {
                        "format_name": info.get("format", {}).get("format_name", "unknown"),
                        "duration": float(info.get("format", {}).get("duration", 0)),
                        "size": int(info.get("format", {}).get("size", 0)),
                        "bit_rate": int(info.get("format", {}).get("bit_rate", 0))
                    },
                    "streams": []
                }
                
                # 处理流信息
                for stream in info.get("streams", []):
                    stream_info = {
                        "index": stream.get("index"),
                        "codec_type": stream.get("codec_type"),
                        "codec_name": stream.get("codec_name")
                    }
                    
                    # 视频特有信息
                    if stream.get("codec_type") == "video":
                        stream_info.update({
                            "width": stream.get("width"),
                            "height": stream.get("height"),
                            "r_frame_rate": stream.get("r_frame_rate"),
                            "display_aspect_ratio": stream.get("display_aspect_ratio", "unknown")
                        })
                    
                    # 音频特有信息
                    elif stream.get("codec_type") == "audio":
                        stream_info.update({
                            "sample_rate": stream.get("sample_rate"),
                            "channels": stream.get("channels"),
                            "channel_layout": stream.get("channel_layout", "unknown")
                        })
                    
                    formatted_info["streams"].append(stream_info)
                
                # 生成人类可读的摘要
                video_streams = [s for s in formatted_info["streams"] if s["codec_type"] == "video"]
                audio_streams = [s for s in formatted_info["streams"] if s["codec_type"] == "audio"]
                
                if video_streams:
                    main_video = video_streams[0]
                    duration_sec = formatted_info["format"]["duration"]
                    minutes = int(duration_sec // 60)
                    seconds = int(duration_sec % 60)
                    
                    summary = f"Video Information for {video_file.filename}:\n\n"
                    summary += f"Format: {formatted_info['format']['format_name']}\n"
                    summary += f"Duration: {minutes}m {seconds}s\n"
                    summary += f"Size: {formatted_info['format']['size'] / (1024*1024):.2f} MB\n"
                    
                    if "width" in main_video and "height" in main_video:
                        summary += f"Resolution: {main_video['width']}x{main_video['height']}\n"
                    
                    summary += f"Video Codec: {main_video.get('codec_name', 'Unknown')}\n"
                    
                    if audio_streams:
                        summary += f"Audio Codec: {audio_streams[0].get('codec_name', 'Unknown')}\n"
                    
                    summary += f"Bitrate: {formatted_info['format']['bit_rate'] / 1000:.2f} kbps\n"
                
                else:
                    summary = f"No video streams found in {video_file.filename}"
                
                # 返回结果
                yield self.create_text_message(summary)
                yield self.create_json_message(formatted_info)
                
            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            error_msg = f"Error processing video file: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "status": "error",
                "message": error_msg
            }) 