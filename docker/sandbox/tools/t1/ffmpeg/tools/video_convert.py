from collections.abc import Generator
from typing import Any
import tempfile
import os
import subprocess
import time
import ffmpeg

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class VideoConvertTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        video_file = tool_parameters.get('video')
        target_format = tool_parameters.get('target_format', '').lower().strip()
        
        # 验证输入
        if not video_file:
            yield self.create_text_message("No video file provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No video file provided"
            })
            return
            
        if not target_format:
            yield self.create_text_message("No target format specified")
            yield self.create_json_message({
                "status": "error",
                "message": "No target format specified"
            })
            return
        
        # 确保格式是合法的
        valid_formats = ["mp4", "avi", "mov", "mkv", "webm", "flv", "wmv", "m4v", "3gp"]
        if target_format not in valid_formats:
            yield self.create_text_message(f"Unsupported format: {target_format}. Supported formats are: {', '.join(valid_formats)}")
            yield self.create_json_message({
                "status": "error",
                "message": f"Unsupported format: {target_format}. Supported formats are: {', '.join(valid_formats)}"
            })
            return
        
        try:
            # 设置临时文件
            input_file_extension = video_file.extension if video_file.extension else '.mp4'
            output_file_extension = f'.{target_format}'
            
            # 获取原始文件名（不带扩展名）
            orig_filename = os.path.splitext(video_file.filename)[0]
            output_filename = f"{orig_filename}{output_file_extension}"
            
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
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=input_file_extension) as in_temp_file:
                in_temp_file.write(video_file.blob)
                in_temp_path = in_temp_file.name
                
            out_temp_path = os.path.join(tempfile.gettempdir(), f"out_{int(time.time())}{output_file_extension}")
            
            try:
                # 执行转换
                yield self.create_text_message(f"Converting video to {target_format} format...")
                
                # 使用ffmpeg-python库进行转换
                (
                    ffmpeg
                    .input(in_temp_path)
                    .output(out_temp_path, **{'c:v': 'copy', 'c:a': 'copy'})
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                
                # 读取输出文件
                with open(out_temp_path, 'rb') as out_file:
                    converted_data = out_file.read()
                
                # 创建结果消息
                yield self.create_blob_message(
                    converted_data,
                    meta={
                        "filename": output_filename,
                        "mime_type": mime_types.get(target_format, f"video/{target_format}"),
                    }
                )
                
                yield self.create_json_message({
                    "status": "success",
                    "message": f"Successfully converted video to {target_format} format",
                    "original_filename": video_file.filename,
                    "converted_filename": output_filename,
                    "target_format": target_format
                })
                
                yield self.create_text_message(f"Successfully converted {video_file.filename} to {target_format} format.")
                
            finally:
                # 清理临时文件
                if os.path.exists(in_temp_path):
                    os.unlink(in_temp_path)
                if os.path.exists(out_temp_path):
                    os.unlink(out_temp_path)
                    
        except Exception as e:
            error_msg = f"Error converting video: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "status": "error",
                "message": error_msg
            }) 