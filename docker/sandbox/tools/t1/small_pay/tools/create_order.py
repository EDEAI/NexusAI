from collections.abc import Generator
from typing import Any
import base64
import logging
import decimal

from dify_plugin.config.logger_format import plugin_logger_handler
import httpx
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(plugin_logger_handler)

class CreateOrderTool(Tool):
    def _get_money(self, money):
        try:
            money_decimal = decimal.Decimal(str(money))
            if not (decimal.Decimal('1.00') <= money_decimal <= decimal.Decimal('200.00')):
                raise ValueError(f"金额 {money} 超出范围 1.00-200.00")
            if money_decimal.as_tuple().exponent < -2:
                raise ValueError(f"金额 {money} 小数位数超过2位")
        except (decimal.InvalidOperation, TypeError):
            raise ValueError(f"无效的金额格式: {money}")
        return int(money_decimal * 100)


    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        money = self._get_money(tool_parameters.get("money"))
        title = tool_parameters.get("title")
        if len(title) > 100:
            raise ValueError(f"订单标题长度 {len(title)}， 超过100个字符")
        desc = tool_parameters.get("desc")
        if desc and len(desc) > 200:
            raise ValueError(f"订单描述长度 {len(desc)}， 超过200个字符")
        
        url = "https://pay.freecicoda.com/smallPayment/api/v1/order/createOrder"
        payload = {
            "apiKey": self.runtime.credentials.get("api_key"),
            "title": title,
            "desc": desc,
            "money": money
        }
        logger.info(f"发送订单参数: {payload}")
        response = httpx.post(url, json=payload).json()
        logger.info(f"创建订单响应: {response}")
        if response.get("code") != 200:
            raise ValueError(response.get("message"))
        
        order_no = response.get("data").get("orderNo")
        if self.session.conversation_id:
            self.session.storage.set(self.session.conversation_id, order_no.encode("utf-8"))
        yield self.create_text_message(order_no)

        b64 = response.get("data").get("qrCodeBase64")
        if ',' in b64:
            prefix, b64 = b64.split(',', 1)
            mime_type = prefix.split(';')[0].split(':')[1]
        else:
            mime_type = 'image/png'
        
        try:
            binary_data = base64.b64decode(b64)
            yield self.create_blob_message(blob=binary_data, meta={"mime_type": mime_type})
        except Exception as e:
            raise ValueError(f"二维码数据解码失败: {str(e)}")
        
