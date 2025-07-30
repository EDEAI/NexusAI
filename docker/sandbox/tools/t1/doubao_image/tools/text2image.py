import base64
from collections.abc import Generator
from openai import OpenAI
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class Text2ImageTool(Tool):
    def _invoke(
        self, tool_parameters: dict
    ) -> Generator[ToolInvokeMessage, None, None]:
        """
        Invoke text-to-image generation tool
        """
        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=self.runtime.credentials.get("api_key"),
            base_url="https://ark.cn-beijing.volces.com/api/v3",
        )
        
        # 获取参数
        prompt = tool_parameters.get("prompt", "")
        if not prompt:
            yield self.create_text_message("请输入提示词")
            return
            
        # 获取尺寸
        size = tool_parameters.get("size", "1024x1024")
        
        # 获取模型
        model = tool_parameters.get("model", "doubao-seedream-3-0-t2i-250415")
        
        # 设置返回格式
        response_format = "b64_json"
        
        try:
            yield self.create_text_message("正在使用豆包 API 生成图像...")
            
            # 调用API
            response = client.images.generate(
                model=model,
                prompt=prompt,
                size=size,
                response_format=response_format,
                n=1,
            )
            
            # 处理结果
            for image in response.data:
                if not image.b64_json:
                    continue
                # 解码图像
                (mime_type, blob_image) = self._decode_image(image.b64_json)
                # 创建二进制消息
                yield self.create_blob_message(
                    blob=blob_image, meta={"mime_type": mime_type}
                )
                yield self.create_text_message("图像生成成功！")
        
        except Exception as e:
            # 处理异常
            yield self.create_text_message(f"生成图像时出错: {str(e)}")

    @staticmethod
    def _decode_image(base64_image: str) -> tuple[str, bytes]:
        """
        Decode a base64 encoded image.
        """
        # 假设图像是纯base64编码
        return ("image/png", base64.b64decode(base64_image))
