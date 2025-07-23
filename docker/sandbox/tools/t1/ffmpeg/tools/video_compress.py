from collections.abc import Generator
from typing import Any
import tempfile
import os
import time
import json
import subprocess
import ffmpeg

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class VideoCompressTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        video_file = tool_parameters.get('video')
        compression_level = tool_parameters.get('compression_level', 'medium').lower()
        
        # 验证输入
        if not video_file:
            yield self.create_text_message("No video file provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No video file provided"
            })
            return
        
        # 验证压缩级别
        valid_levels = ['low', 'medium', 'high']
        if compression_level not in valid_levels:
            yield self.create_text_message(f"Invalid compression level: {compression_level}. Using 'medium' instead.")
            compression_level = 'medium'
        
        try:
            # 设置临时文件
            file_extension = video_file.extension if video_file.extension else '.mp4'
            format_type = file_extension.lstrip('.')
            
            # 获取原始文件名（不带扩展名）
            orig_filename = os.path.splitext(video_file.filename)[0]
            output_filename = f"{orig_filename}_compressed{file_extension}"
            
            # 设置MIME类型映射
            mime_types = {
                'mp4': 'video/mp4',
                'avi': 'video/x-msvideo',
                'mov': 'video/quicktime',
                'mkv': 'video/x-matroska',
                'webm': 'video/webm',
                'flv': 'video/x-flv',
                'wmv': 'video/x-ms-wmv',
                'm4v': 'video/x-m4v',
                '3gp': 'video/3gpp'
            }
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as in_temp_file:
                in_temp_file.write(video_file.blob)
                in_temp_path = in_temp_file.name
                
            out_temp_path = os.path.join(tempfile.gettempdir(), f"compressed_{int(time.time())}{file_extension}")
            
            try:
                # 获取原始视频信息
                probe = ffmpeg.probe(in_temp_path)
                
                # 获取原始文件大小
                original_size = os.path.getsize(in_temp_path)
                
                # 根据压缩级别设置参数
                if compression_level == 'low':
                    crf = 23
                    preset = 'medium'
                elif compression_level == 'medium':
                    crf = 28
                    preset = 'medium'
                else:  # high
                    crf = 32
                    preset = 'faster'
                
                # 执行压缩
                yield self.create_text_message(f"Compressing video with {compression_level} compression level...")
                
                # 使用ffmpeg-python库进行压缩
                (
                    ffmpeg
                    .input(in_temp_path)
                    .output(out_temp_path, crf=crf, preset=preset)
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                
                # 获取压缩后文件大小
                compressed_size = os.path.getsize(out_temp_path)
                reduction_percent = ((original_size - compressed_size) / original_size) * 100
                
                # 读取输出文件
                with open(out_temp_path, 'rb') as out_file:
                    compressed_data = out_file.read()
                
                # 创建结果消息
                yield self.create_blob_message(
                    compressed_data,
                    meta={
                        "filename": output_filename,
                        "mime_type": mime_types.get(format_type, f"video/{format_type}"),
                    }
                )
                
                yield self.create_json_message({
                    "status": "success",
                    "message": f"Successfully compressed video with {compression_level} compression level",
                    "original_filename": video_file.filename,
                    "compressed_filename": output_filename,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "size_reduction_percent": reduction_percent,
                    "compression_level": compression_level
                })
                
                # 生成人类可读的摘要
                summary = f"Successfully compressed {video_file.filename}\n\n"
                summary += f"Original Size: {original_size / (1024*1024):.2f} MB\n"
                summary += f"Compressed Size: {compressed_size / (1024*1024):.2f} MB\n"
                summary += f"Size Reduction: {reduction_percent:.2f}%\n"
                summary += f"Compression Level: {compression_level}"
                
                yield self.create_text_message(summary)
                
            finally:
                # 清理临时文件
                if os.path.exists(in_temp_path):
                    os.unlink(in_temp_path)
                if os.path.exists(out_temp_path):
                    os.unlink(out_temp_path)
                    
        except Exception as e:
            error_msg = f"Error compressing video: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "status": "error",
                "message": error_msg
            })