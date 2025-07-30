from collections.abc import Generator
from typing import Any
import logging
import time

from dify_plugin.config.logger_format import plugin_logger_handler
import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

ORDER_STATUS_MAP = {
    0: "未支付",
    1: "支付成功",
    2: "支付失败",
    3: "已过期",
    4: "订单取消",
    5: "订单退款"
}

class QueryOrderTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        order_no = tool_parameters.get("order_no")
        if not order_no and self.session.storage.exist(self.session.conversation_id):
            order_no = self.session.storage.get(self.session.conversation_id).decode("utf-8")
        if not order_no:
            raise ValueError("未获取到订单号")
        
        url = "https://pay.freecicoda.com/smallPayment/api/v1/order/queryOrder"
        payload = {
            "apiKey": self.runtime.credentials.get("api_key"),
            "orderNo": order_no
        }
        logger.info(f"发送订单参数: {payload}")
        response = httpx.get(url, params=payload).json()
        logger.info(f"查询订单响应: {response}")
        if response.get("code") != 200:
            raise ValueError(response.get("message"))
        
        status = response.get("data").get("status")
        count = 0 
        while status == 0:
            time.sleep(1)
            count += 1
            if count > 120:
                logger.info(f"订单超时未支付")
                break
            response = httpx.get(url, params=payload).json()
            status = response.get("data").get("status")
        order_status = ORDER_STATUS_MAP.get(status, "未知状态")
        yield self.create_text_message(order_status)
        yield self.create_json_message(response)
        