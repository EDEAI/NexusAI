import time
import base64
import traceback
from collections.abc import Generator
from typing import Any, Union
import requests
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class Image2VideoTool(Tool):
    def _encode_image(self, file_data):
        """将图片文件编码为base64"""
        try:
            # 记录图片大小
            image_size = len(file_data) / 1024  # KB
            encoded = base64.b64encode(file_data).decode("utf-8")
            encoded_size = len(encoded) / 1024  # KB
            debug_info = f"图片编码完成: 原始大小={image_size:.2f}KB, 编码后大小={encoded_size:.2f}KB"
            return encoded, debug_info
        except Exception as e:
            stack_trace = traceback.format_exc()
            raise Exception(f"图片编码失败: {str(e)}\n堆栈跟踪: {stack_trace}")

    def _invoke(
        self, tool_parameters: dict
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke image-to-video generation tool using Doubao AI
        
        Parameters:
            tool_parameters (dict): Dictionary containing:
                - prompt (str): Text description for video generation
                - image (file): Image file to be used for video generation
                - duration (str): Video duration in seconds
                - ratio (str): Aspect ratio (e.g., "16:9")
        
        Returns:
            Generator[ToolInvokeMessage, None, None]: Messages including video generation progress and final video URL
        """
        # 获取API key
        api_key = self.runtime.credentials.get("api_key")
        base_url = "https://ark.cn-beijing.volces.com/api/v3"
        
        # 获取参数
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("请输入视频描述提示词")
            return
            
        # 获取图片文件
        image_file = tool_parameters.get("image")
        if not image_file:
            yield self.create_text_message("请上传图片文件")
            return
        
        # 处理图片文件
        try:
            # 处理不同类型的图片输入
            file_content = None
            
            # 检查文件类型并获取文件内容
            if hasattr(image_file, 'url') and image_file.url:
                # 如果文件是通过URL提供的
                file_url = image_file.url
                yield self.create_text_message(f"正在从URL获取图片: {file_url[:30]}...")
                try:
                    response = requests.get(file_url, timeout=60)
                    response.raise_for_status()
                    file_content = response.content
                    yield self.create_text_message(f"成功下载图片: 大小={len(file_content)/1024:.2f}KB")
                except Exception as e:
                    yield self.create_text_message(f"从URL下载图片失败: {str(e)}")
                    return
            
            # 如果URL下载失败或没有URL，尝试其他方法
            if file_content is None and hasattr(image_file, 'blob'):
                try:
                    file_content = image_file.blob
                    yield self.create_text_message(f"从blob属性获取文件数据: 大小={len(image_file.blob)/1024:.2f}KB")
                except Exception as e:
                    yield self.create_text_message(f"获取blob属性失败: {str(e)}")
            
            # 尝试从read方法获取
            if file_content is None and hasattr(image_file, 'read'):
                try:
                    file_content = image_file.read()
                    yield self.create_text_message("从可读对象获取文件数据")
                    # 如果是文件对象，可能需要重置文件指针
                    if hasattr(image_file, 'seek'):
                        image_file.seek(0)
                except Exception as e:
                    yield self.create_text_message(f"从read方法获取文件数据失败: {str(e)}")
            
            # 尝试作为文件路径处理
            if file_content is None and isinstance(image_file, str):
                try:
                    with open(image_file, 'rb') as f:
                        file_content = f.read()
                    yield self.create_text_message(f"从文件路径获取文件数据: {image_file}, 大小={len(file_content)/1024:.2f}KB")
                except (TypeError, IOError) as e:
                    yield self.create_text_message(f"从文件路径获取文件数据失败: {str(e)}")
            
            # 尝试本地文件缓存方式
            if file_content is None and hasattr(image_file, 'path'):
                try:
                    with open(image_file.path, 'rb') as f:
                        file_content = f.read()
                    yield self.create_text_message(f"从本地缓存路径获取文件数据: {image_file.path}, 大小={len(file_content)/1024:.2f}KB")
                except (TypeError, IOError) as e:
                    yield self.create_text_message(f"从本地缓存路径获取文件数据失败: {str(e)}")
            
            # 如果所有方法都失败
            if file_content is None:
                yield self.create_text_message("无法获取图片数据。请尝试重新上传图片或使用较小的图片文件")
                return
            
            # 编码图片数据为base64
            try:
                encoded_image, encoding_debug = self._encode_image(file_content)
                yield self.create_text_message(encoding_debug)
                
                # 构建图片URL (豆包API需要可访问的URL或base64数据)
                image_data_url = f"data:image/jpeg;base64,{encoded_image}"
            except Exception as e:
                yield self.create_text_message(f"图片编码失败: {str(e)}")
                return
                
        except Exception as e:
            stack_trace = traceback.format_exc()
            yield self.create_text_message(f"处理图片文件失败: {str(e)}\n堆栈跟踪:\n{stack_trace}")
            return
        
        # 获取比例
        ratio = tool_parameters.get("ratio", "16:9")
        # 添加比例参数到提示词
        if ratio and not "--ratio" in prompt:
            prompt = f"{prompt} --ratio adaptive"  # 始终使用adaptive而不是用户选择的ratio值
        
        # 获取时长
        duration = tool_parameters.get("duration", "5")
        # 添加时长参数到提示词
        if duration and not "--duration" in prompt and not "--dur" in prompt:
            prompt = f"{prompt} --duration {duration}"
        
        # 使用图生视频模型
        model = "doubao-seedance-1-0-lite-i2v-250428"
        
        try:
            # 显示正在使用的模型
            yield self.create_text_message("正在使用豆包 Seedance 图生视频模型生成视频...")
            
            # 设置请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            # 创建请求内容
            content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": image_data_url
                    }
                }
            ]
            
            # 请求数据
            request_data = {
                "model": model,
                "content": content
            }
            
            # 发送请求
            yield self.create_text_message("正在创建视频生成任务...")
            
            response = requests.post(
                f"{base_url}/contents/generations/tasks",
                headers=headers,
                json=request_data
            )
            
            if response.status_code != 200:
                yield self.create_text_message(f"创建视频生成任务失败，状态码: {response.status_code}, 错误信息: {response.text}")
                return
                
            # 获取任务ID
            response_json = response.json()
            task_id = response_json.get("id")
            if not task_id:
                yield self.create_text_message("创建视频生成任务失败，未获取到任务ID")
                return
                
            # 显示任务信息
            yield self.create_text_message(f"视频生成任务已创建，任务ID: {task_id}")
            yield self.create_text_message(f"提示词: {prompt}")
            yield self.create_text_message("正在等待视频生成完成...")
            
            # 轮询查询任务状态，直到完成或失败
            max_retries = 60  # 最大重试次数，防止无限等待
            retry_count = 0
            video_url = None
            
            while retry_count < max_retries:
                # 等待一段时间再查询
                time.sleep(5)
                
                # 查询任务状态
                task_response = requests.get(
                    f"{base_url}/contents/generations/tasks/{task_id}",
                    headers=headers
                )
                
                if task_response.status_code != 200:
                    yield self.create_text_message(f"查询视频生成任务失败，状态码: {task_response.status_code}, 错误信息: {task_response.text}")
                    return
                    
                task_data = task_response.json()
                
                # 检查任务状态
                status = task_data.get("status")
                
                if status == "succeeded":
                    # 任务成功，获取视频URL
                    video_url = task_data.get("content", {}).get("video_url")
                    break
                elif status == "failed":
                    # 任务失败
                    error_message = task_data.get("error", {}).get("message", "未知错误")
                    yield self.create_text_message(f"视频生成任务失败: {error_message}")
                    return
                elif status == "canceled":
                    # 任务被取消
                    yield self.create_text_message("视频生成任务已被取消")
                    return
                
                # 继续等待
                yield self.create_text_message(f"视频正在生成中，已等待 {(retry_count + 1) * 5} 秒...")
                retry_count += 1
            
            # 检查是否获取到视频URL
            if video_url:
                yield self.create_text_message("视频生成成功！")
                # 直接显示视频
                yield self.create_image_message(video_url)
                yield self.create_text_message("上方视频链接有效期为24小时。如需保存，请在此期间内下载视频文件。")
            else:
                yield self.create_text_message("视频生成超时或失败，请稍后再试")
        
        except Exception as e:
            # 处理异常
            yield self.create_text_message(f"生成视频时出错: {str(e)}")
