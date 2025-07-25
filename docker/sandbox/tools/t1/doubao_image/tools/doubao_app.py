import os
from typing import Any, Dict, Optional, Union

from openai import OpenAI

class DoubaoApp:
    """
    Doubao API client for text-to-image generation using OpenAI client
    """
    def __init__(
        self, 
        api_key: str, 
        api_secret: str = None,  # 不需要使用，但保留参数以保持接口兼容性
        region: str = "cn-north-1"
    ):
        """
        Initialize the Doubao API client.
        
        Args:
            api_key: Volcengine API key
            api_secret: Not used in OpenAI client mode
            region: Not used in OpenAI client mode
        """
        self.api_key = api_key
        self.client = OpenAI(
            base_url="https://ark.cn-beijing.volces.com/api/v3",
            api_key=self.api_key,
        )
        
        if not self.api_key:
            raise ValueError("API key is required")

    def generate_image(
        self,
        prompt: str,
        model: str = "doubao-seedream-3-0-t2i-250415",
        size: str = "1024x1024",
        seed: int = None,
        guidance_scale: float = None,
        watermark: bool = False,
        quality: str = "standard",
        response_format: str = "url",
    ) -> Dict[str, Any]:
        """
        Generate image from text using Doubao API with OpenAI client.
        
        Args:
            prompt: Text prompt for image generation
            model: Model name/version to use
            size: Image size in format "widthxheight"
            seed: Random seed for generation
            guidance_scale: How closely to follow the prompt
            watermark: Whether to add a watermark (ignored - not supported in standard OpenAI client)
            quality: Generation quality ("standard" or "hd")
            response_format: Return format ("url" or "b64_json")
            
        Returns:
            Dictionary containing the generated image URL or base64 data
        """
        try:
            # 准备参数
            params = {
                "model": model,
                "prompt": prompt,
                "size": size,
                "response_format": response_format,
                "n": 1  # 生成图片数量
            }
            
            # 添加可选参数（如果不是None）
            if seed is not None and seed != -1:
                params["seed"] = seed
                
            if guidance_scale is not None:
                # 注意：标准OpenAI客户端不支持guidance_scale参数
                # 但我们可以在请求头或自定义参数中添加
                pass
                
            # 注意：watermark参数在标准OpenAI客户端中不受支持
            # 如需支持，可能需要使用火山引擎自己的SDK或直接HTTP请求
            
            # 调用图像生成API
            response = self.client.images.generate(**params)
            
            # 处理返回结果
            if response.data and len(response.data) > 0:
                if response_format == "url":
                    return {"url": response.data[0].url}
                else:
                    return {"b64_json": response.data[0].b64_json}
            else:
                return {"error": {"message": "No image data returned"}}
                
        except Exception as e:
            # 处理错误
            return {"error": {"message": str(e)}}
            
    # 保留旧方法以便兼容性
    def text2image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        seed: int = None,
        scale: float = None,
        use_pre_llm: bool = None,
        return_url: bool = True,
        logo_info: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Legacy method for compatibility"""
        size = f"{width}x{height}"
        response_format = "url" if return_url else "b64_json"
        
        result = self.generate_image(
            prompt=prompt,
            size=size,
            seed=seed,
            guidance_scale=scale,
            response_format=response_format
        )
        
        # 转换为旧格式
        if "url" in result:
            return {
                "code": 10000,
                "data": {
                    "image_urls": [result["url"]],
                    "binary_data_base64": [],
                    "algorithm_base_resp": {"status_code": 0, "status_message": "Success"}
                },
                "message": "Success"
            }
        elif "b64_json" in result:
            return {
                "code": 10000,
                "data": {
                    "image_urls": [],
                    "binary_data_base64": [result["b64_json"]],
                    "algorithm_base_resp": {"status_code": 0, "status_message": "Success"}
                },
                "message": "Success"
            }
        else:
            return {
                "code": 50000,
                "message": result.get("error", {}).get("message", "Unknown error"),
                "data": {}
            }
