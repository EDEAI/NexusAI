from collections.abc import Generator
from typing import Any
import tempfile
import os
import time
import re
import ffmpeg

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

class VideoTrimTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        video_file = tool_parameters.get('video')
        start_time = tool_parameters.get('start_time', '')
        end_time = tool_parameters.get('end_time', '')
        
        # 验证输入
        if not video_file:
            yield self.create_text_message("No video file provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No video file provided"
            })
            return
        
        if not start_time:
            yield self.create_text_message("No start time provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No start time provided"
            })
            return
        
        if not end_time:
            yield self.create_text_message("No end time provided")
            yield self.create_json_message({
                "status": "error",
                "message": "No end time provided"
            })
            return
        
        # 解析时间格式
        try:
            start_seconds = self._parse_time(start_time)
            end_seconds = self._parse_time(end_time)
            
            if start_seconds >= end_seconds:
                yield self.create_text_message("Start time must be before end time")
                yield self.create_json_message({
                    "status": "error",
                    "message": "Start time must be before end time"
                })
                return
                
        except ValueError as e:
            yield self.create_text_message(str(e))
            yield self.create_json_message({
                "status": "error",
                "message": str(e)
            })
            return
        
        try:
            # 设置临时文件
            file_extension = video_file.extension if video_file.extension else '.mp4'
            format_type = file_extension.lstrip('.')
            
            # 获取原始文件名（不带扩展名）
            orig_filename = os.path.splitext(video_file.filename)[0]
            output_filename = f"{orig_filename}_trimmed{file_extension}"
            
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
                
            out_temp_path = os.path.join(tempfile.gettempdir(), f"trimmed_{int(time.time())}{file_extension}")
            
            try:
                # 执行剪切
                yield self.create_text_message(f"Trimming video from {start_time} to {end_time}...")
                
                # 使用ffmpeg-python库进行剪切
                (
                    ffmpeg
                    .input(in_temp_path, ss=start_seconds, to=end_seconds)
                    .output(out_temp_path, c='copy')
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                
                # 读取输出文件
                with open(out_temp_path, 'rb') as out_file:
                    trimmed_data = out_file.read()
                
                # 创建结果消息
                yield self.create_blob_message(
                    trimmed_data,
                    meta={
                        "filename": output_filename,
                        "mime_type": mime_types.get(format_type, f"video/{format_type}"),
                    }
                )
                
                yield self.create_json_message({
                    "status": "success",
                    "message": f"Successfully trimmed video from {start_time} to {end_time}",
                    "original_filename": video_file.filename,
                    "trimmed_filename": output_filename,
                    "start_time": start_time,
                    "end_time": end_time,
                    "duration": end_seconds - start_seconds
                })
                
                yield self.create_text_message(f"Successfully trimmed video from {start_time} to {end_time}. New duration: {end_seconds - start_seconds:.2f} seconds.")
                
            finally:
                # 清理临时文件
                if os.path.exists(in_temp_path):
                    os.unlink(in_temp_path)
                if os.path.exists(out_temp_path):
                    os.unlink(out_temp_path)
                    
        except Exception as e:
            error_msg = f"Error trimming video: {str(e)}"
            yield self.create_text_message(error_msg)
            yield self.create_json_message({
                "status": "error",
                "message": error_msg
            })
    
    def _parse_time(self, time_str):
        """解析时间字符串，支持HH:MM:SS格式和秒数"""
        # 尝试解析HH:MM:SS格式
        if re.match(r'^\d+:\d+:\d+$', time_str):
            hours, minutes, seconds = map(int, time_str.split(':'))
            return hours * 3600 + minutes * 60 + seconds
            
        # 尝试解析MM:SS格式
        elif re.match(r'^\d+:\d+$', time_str):
            minutes, seconds = map(int, time_str.split(':'))
            return minutes * 60 + seconds
            
        # 尝试解析纯秒数
        elif time_str.isdigit() or (time_str.replace('.', '', 1).isdigit() and time_str.count('.') < 2):
            return float(time_str)
            
        else:
            raise ValueError(f"Invalid time format: {time_str}. Use HH:MM:SS, MM:SS or seconds.") 