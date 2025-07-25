from collections.abc import Generator
from typing import Any
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from chuangsiai_sdk import  ChuangsiaiClient


class LLMOutputSafetyGuardrailsTool(Tool):
    """
    安全护栏输出检测工具类
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """
        根据输入的监测内容和策略KEY，调用创思安全护栏接口进行内容安全检测。
        该工具将内容和策略KEY作为输入参数，返回安全护栏检测结果。

        Args:
            tool_parameters: 一个包含工具输入参数的字典:
                - content (str):  需要检测的内容。
                - strategy_id (str):  安全护栏策略标识。

        Yields:
            ToolInvokeMessage: 包含安全护栏检测结果的消息。

        Raises:
            Exception: 如果凭证无效或请求失败，将抛出异常。
        """
        # 1. 从运行时获取凭证
        try:
            access_key = self.runtime.credentials["chuangsi_access_key"]
            secret_key = self.runtime.credentials["chuangsi_secret_key"]
        except KeyError:
            # raise Exception("AccessKey 或 SecretKey 未配置或无效。请在插件设置中提供。")
            raise Exception("AccessKey or SecretKey is not configured or invalid. Please provide it in the plugin settings.")

        # 2. 获取工具输入参数
        content = tool_parameters.get("content", "") # 使用 .get 提供默认值
        strategy_id = tool_parameters.get("strategy_id", "")

        if not strategy_id:
            raise Exception("The strategy ID cannot be empty. Please provide a valid strategy ID.")

        # 1. 初始化签名工具
        headers={ "X-Referer":"dify" }
        client = ChuangsiaiClient(access_key=access_key,secret_key=secret_key,headers=headers)
        try:
            # 2. 调用接口
            resp = client.output_guardrail(strategy_id=strategy_id, content=content)
            # raise Exception(f"模拟调用安全护栏失败")
        except Exception as e:
            # 如果库调用失败，抛出异常
            raise Exception(f"调用安全护栏失败: {e}")

        # print("请求结果:", response_data)
        # if response_data.get("code") == 0:
        #     print("✅ 请求成功:", response_data)
        # else:
        #     print("❌ 请求错误:", response_data)

  
        # # 文本输出
        # yield self.create_text_message("这是文本消息")
        # # JSON输出
        # yield self.create_json_message({"key": "value"})
        # # 链接输出
        # yield self.create_link_message("https://example.com")
        # # 变量输出 (用于工作流)
        # yield self.create_variable_message("variable_name", "variable_value")
        # 4. 返回结果
        yield self.create_json_message(resp)