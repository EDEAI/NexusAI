from collections.abc import Generator
from typing import Any
from PIL import Image
import io
import uuid
import datetime
import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File


class ImageCompressionTool(Tool):

    def calculate_compression_quality(self, original_size: int, target_size_mb: float) -> int:
        """
        根据原图大小和目标大小计算合适的压缩质量
        
        :param original_size: 原图大小（字节）
        :param target_size_mb: 目标大小（MB）
        :return: 压缩质量（1-100）
        """
        # 将目标大小从MB转换为字节
        target_size_bytes = target_size_mb * 1024 * 1024
        
        # 只有当原图大于目标大小时才进行压缩
        if target_size_mb > 0 and original_size > target_size_bytes:
            # 计算压缩质量 - 按照原始大小和目标大小的比例计算
            quality = int(100 * target_size_bytes / original_size)
            # 限制压缩质量范围
            if quality < 1:
                quality = 1
            elif quality > 100:
                quality = 100
        else:
            # 如果原图已经小于目标大小，使用较高的质量保持原样
            quality = 95
            
        return quality

    def compress_image(self, image_file: bytes, quality: int = 85) -> dict[str, str | int | bytes]:
        """
        压缩图片文件

        :param image_file: 图片文件的字节流
        :param quality: 压缩质量（1-100），默认 85
        :return: 压缩后的图片信息字典，包含文件内容、格式、大小和生成的唯一文件名
        """
        try:
            # 打开图片
            with Image.open(io.BytesIO(image_file)) as img:
                print("Image compression started")

                # 获取图片格式，如果没有格式则默认为JPEG
                img_format = getattr(img, 'format', 'JPEG')
                if not img_format:
                    img_format = 'JPEG'
                
                # 生成唯一的文件名
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]  # 使用UUID前8位以保持文件名简短
                filename = f"compressed_{timestamp}_{unique_id}.{img_format.lower()}"
                
                # 创建字节流缓冲区
                output = io.BytesIO()
                
                # 根据不同的图片格式采用不同的压缩策略
                if img_format.upper() == 'PNG':
                    # PNG格式特殊处理
                    return self.compress_png(img, quality, filename)
                else:
                    # 非PNG格式处理（如JPEG）
                    # 转换为 RGB 模式（如果不是）
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # 保存压缩后的图片到缓冲区
                    img.save(output, format=img_format, quality=quality)
                    output.seek(0)
                    
                    return {
                        "file": output.read(),
                        "format": img_format,
                        "size": len(output.getvalue()),
                        "filename": filename
                    }
        except Exception as e:
            raise ValueError(f"Image compression failed: {str(e)}")

    def compress_png(self, img, quality: int, filename: str) -> dict[str, str | int | bytes]:
        """
        专门处理PNG图片的压缩
        
        :param img: PIL Image对象
        :param quality: 压缩质量参数
        :param filename: 输出文件名
        :return: 压缩后的图片信息字典
        """
        # PNG的质量参数实际上是压缩级别(0-9)
        # 将1-100的质量值映射到0-9的压缩级别
        if quality <= 10:
            compress_level = 9  # 最高压缩率
        else:
            compress_level = 9 - min(9, int(quality / 10))
        
        # 准备输出缓冲区
        output = io.BytesIO()
        
        # 保存原始尺寸，用于判断是否需要缩小
        orig_width, orig_height = img.size
        has_alpha = img.mode == 'RGBA'
        
        # 对于大尺寸PNG，尝试减小尺寸
        max_dimension = 1500  # 降低为1500以获得更好的压缩率
        if max(orig_width, orig_height) > max_dimension:
            ratio = max_dimension / max(orig_width, orig_height)
            new_width = int(orig_width * ratio)
            new_height = int(orig_height * ratio)
            img = img.resize((new_width, new_height), Image.LANCZOS)
        
        # 针对不同类型的PNG使用不同策略
        if has_alpha:
            # 有透明通道的PNG保留RGBA模式
            # 但可以尝试减少颜色数量，对于质量较低的要求，可以量化颜色
            if quality < 50:
                # 减少调色板颜色数量来显著降低文件大小
                # 使用Floyd-Steinberg抖动算法，保持视觉效果
                img = img.convert('RGBA').quantize(colors=256, method=2, kmeans=1, dither=Image.FLOYDSTEINBERG)
                img = img.convert('RGBA')  # 量化后转回RGBA以保留透明度
        else:
            # 无透明通道的PNG可以考虑转为RGB并量化颜色
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 对于低质量需求，进行颜色量化
            if quality < 60:
                colors = 256 if quality > 30 else 128
                img = img.quantize(colors=colors, method=2, kmeans=1, dither=Image.FLOYDSTEINBERG)
                img = img.convert('RGB')  # 转回RGB模式以保持兼容性
        
        # 尝试用不同参数保存并选择最小的结果
        attempts = []
        
        # 第一种尝试: 标准优化PNG
        standard_output = io.BytesIO()
        img.save(standard_output, 
                format='PNG', 
                optimize=True,
                compress_level=compress_level)
        attempts.append(standard_output.getvalue())
        
        # 第二种尝试: 降低位深度（如果质量要求低）
        if quality < 50:
            reduced_output = io.BytesIO()
            if not has_alpha:  # 无透明通道时可以使用P模式
                try:
                    # 减少到256色会显著降低文件大小
                    img_p = img.convert('P', palette=Image.ADAPTIVE, colors=256)
                    img_p.save(reduced_output, format='PNG', optimize=True, compress_level=compress_level)
                    attempts.append(reduced_output.getvalue())
                except Exception:
                    pass
        
        # 选择最小的输出
        best_result = min(attempts, key=len)
        
        return {
            "file": best_result,
            "format": "PNG",
            "size": len(best_result),
            "filename": filename
        }

    def iterative_compress_image(self, image_file: bytes, target_size_bytes: int, 
                              initial_quality: int = 85, max_iterations: int = 5) -> dict[str, str | int | bytes]:
        """
        通过多次尝试迭代压缩图片，直到达到或接近目标大小
        
        :param image_file: 图片文件的字节流
        :param target_size_bytes: 目标大小（字节）
        :param initial_quality: 初始压缩质量
        :param max_iterations: 最大尝试次数
        :return: 压缩后的图片信息字典
        """
        # 如果原图就小于目标大小，直接返回原图
        if len(image_file) <= target_size_bytes:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            return {
                "file": image_file,
                "format": "JPEG",  # 默认格式
                "size": len(image_file),
                "filename": f"original_{timestamp}_{unique_id}.jpg",
                "compressed": False
            }
        
        # 打开图片获取格式
        with Image.open(io.BytesIO(image_file)) as img:
            img_format = getattr(img, 'format', 'JPEG')
            if not img_format:
                img_format = 'JPEG'
            
            # PNG格式特殊处理：多级压缩尝试
            if img_format.upper() == 'PNG':
                # 第一级尝试：最高压缩级别的PNG
                result = self.compress_image(image_file, quality=5)
                
                # 如果还是太大，尝试第二级压缩（更激进的量化）
                if result.get("size") > target_size_bytes * 1.2:
                    try:
                        # 尝试更激进的压缩设置
                        secondary_result = self.compress_image(image_file, quality=1)
                        if secondary_result.get("size") < result.get("size"):
                            result = secondary_result
                    except Exception:
                        pass  # 如果失败，继续使用之前的结果
                
                # 第三级尝试：对于无透明通道的PNG，考虑转换为JPEG
                if result.get("size") > target_size_bytes and img.mode != "RGBA":
                    try:
                        output = io.BytesIO()
                        img_rgb = img.convert("RGB")
                        
                        # 用适中质量保存为JPEG
                        jpeg_quality = min(70, int(70 * target_size_bytes / result.get("size")))
                        img_rgb.save(output, format="JPEG", quality=max(jpeg_quality, 40))
                        output.seek(0)
                        
                        jpeg_size = len(output.getvalue())
                        # 只有当JPEG显著小于PNG时才使用JPEG
                        if jpeg_size < result.get("size") * 0.8:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            unique_id = str(uuid.uuid4())[:8]
                            return {
                                "file": output.getvalue(),
                                "format": "JPEG",
                                "size": jpeg_size,
                                "filename": f"compressed_{timestamp}_{unique_id}.jpg"
                            }
                    except Exception:
                        pass  # 如果转换失败，继续使用PNG结果
                
                return result
        
        # 初始质量设置
        quality = initial_quality
        min_quality = 1
        max_quality = 100
        best_result = None
        
        # 迭代压缩
        for i in range(max_iterations):
            try:
                result = self.compress_image(image_file, quality=quality)
                
                # 记录最佳结果（离目标最近但不超过）
                current_size = result.get("size")
                if best_result is None or (current_size <= target_size_bytes and current_size > best_result.get("size")):
                    best_result = result
                
                # 达到目标，提前退出
                if abs(current_size - target_size_bytes) / target_size_bytes < 0.05:  # 在5%误差范围内接受
                    return result
                
                # 二分法调整质量
                if current_size > target_size_bytes:
                    max_quality = quality
                    quality = (min_quality + quality) // 2
                else:
                    min_quality = quality
                    quality = (quality + max_quality) // 2
                
                # 如果质量调整幅度太小，提前退出
                if max_quality - min_quality <= 3:
                    break
                    
            except Exception as e:
                print(f"Iterative compression attempt {i+1} fail: {str(e)}")
                break
        
        # 如果没有任何成功压缩的结果，返回最后一次尝试
        return best_result if best_result else self.compress_image(image_file, quality=min_quality)

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        imgs = tool_parameters.get("input_image")
        host_url = tool_parameters.get("host_url")
        target_size = tool_parameters.get("target_size")
        if not imgs:
            yield self.create_json_message(
                {
                    "result": "please provide image file"
                }
            )
            return
        if not isinstance(imgs, list):
            yield self.create_json_message({
                "result": "please provide image file list"
            })
            return
        for img in imgs:
            # 获取正确的字节流数据
            if isinstance(img, File):
                try:
                    # 先判断File mime 是否为图片类型
                    if img.mime_type not in ["image/jpeg", "image/png", "image/gif", "image/webp", "image/bmp"]:
                        yield self.create_json_message({
                            "result": f"Unsupported file type: {img.mime_type}"
                        })
                        continue
                    url = img.url
                    if not url.startswith(('http://', 'https://')):
                        # 去掉末尾的斜杠
                        host_url = host_url.rstrip('/')
                        url = f"{host_url}/{url}"
                    # 下载图片
                    response = requests.get(url)
                    response.raise_for_status()
                    input_image_bytes = response.content
                    # input_image_bytes = img.blob
                except Exception as e:
                    yield self.create_json_message({
                        "result": f"Failed to download image: {str(e)}"
                    })
                    continue
            elif isinstance(img, bytes):
                input_image_bytes = img
            else:
                yield self.create_json_message({
                    "result": f"Unsupported image format: {type(img)}"
                })
                continue

            original_size = len(input_image_bytes)
            target_size_bytes = target_size * 1024 * 1024
            
            # 使用迭代压缩方法
            if target_size > 0 and original_size > target_size_bytes:
                initial_quality = self.calculate_compression_quality(original_size, target_size)
                compressed_img = self.iterative_compress_image(
                    input_image_bytes, 
                    target_size_bytes, 
                    initial_quality=initial_quality
                )
            else:
                # 如果原图已经小于目标大小，使用高质量压缩或保持原样
                compressed_img = self.compress_image(input_image_bytes, quality=95)
            
            # 如果压缩后的大小反而大于原始大小，则使用原始图片
            if compressed_img.get("size") > original_size:
                meta = {
                    "filename": img.filename if isinstance(img, File) else "original_image.jpg",
                    "mime_type": img.mime_type if isinstance(img, File) else "image/jpeg",
                    "size": original_size,
                }
                yield self.create_blob_message(input_image_bytes, meta)
            else:
                meta = {
                    "filename": compressed_img.get("filename", "compressed_image.jpg"), 
                    "mime_type": f"image/{compressed_img.get('format').lower()}" if compressed_img.get('format') else img.mime_type if isinstance(img, File) else "image/jpeg",
                    "size": compressed_img.get("size"),
                }
                yield self.create_blob_message(compressed_img.get("file"), meta)

