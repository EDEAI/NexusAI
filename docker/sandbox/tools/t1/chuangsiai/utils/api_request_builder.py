import hmac
import hashlib
import json
from urllib.parse import quote
import time
import uuid

class ApiRequestBuilder:
    """
    公共请求头生成工具（Python版）
    """
    
    def __init__(self, access_key, secret_key):
        """
        初始化配置
        :param access_key: 控制台获取的AccessKey
        :param secret_key: 控制台获取的SecretKey
        """
        self.access_key = access_key
        self.secret_key = secret_key
    
    def _generate_signature(self, method, url, body, timestamp, nonce):
        """
        生成签名（内部方法）
        :param method: HTTP方法（如POST）
        :param url: 请求路径（如/api/verify）
        :param body: 请求体对象（需严格JSON格式化）
        :param timestamp: 时间戳（毫秒）
        :param nonce: 随机字符串（10-40位）
        :return: 签名字符串
        """
        # 1. 确保JSON无多余空格并URL编码 - json.dumps 默认使用 ascii 编码，需要指定 ensure_ascii=False，并且 separators=(',', ':') 可以去掉 json 字符串中的空格
        body_string = quote(json.dumps(body, ensure_ascii=False, separators=(',', ':')))
        # 2. 拼接待签名字符串（严格按顺序）
        string_to_sign = f"{method}\n{url}\n{body_string}\n{timestamp}\n{nonce}"
        # 3. 使用HMAC-SHA256加密并转为十六进制
        hmac_obj = hmac.new(
            self.secret_key.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            hashlib.sha256
        )
        return hmac_obj.hexdigest()
    
    def build_headers(self, method, url, body, timestamp=None, nonce=None):
        """
        生成完整请求头（含签名）
        :param method: HTTP方法
        :param url: 请求路径
        :param body: 请求体
        :param timestamp: 可选时间戳，默认当前时间
        :param nonce: 可选随机字符串，默认自动生成UUID
        :return: 公共请求头字典
        """
        ts = timestamp or str(int(time.time() * 1000))
        nc = nonce or str(uuid.uuid4())  # 此处可使用自定义随机数生成
        signature = self._generate_signature(method, url, body, ts, nc)
        return {
            'X-Timestamp': ts,
            'X-Nonce': nc,
            'Content-Type': 'application/json',
            'Authorization': f"{self.access_key}:{signature}",
            'X-Referer': 'dify',
        }


# # 示例用法
# if __name__ == '__main__':
#     builder = ApiRequestBuilder(
#         'ak_0f77303296f58fbfa4f158432e8',  # AccessKey
#         'sk_88674930cb0780033704aa05e8967*******'  # SecretKey
#     )
#     headers = builder.build_headers(
#         'POST',
#         '/api/verify',
#         {'content': 'test'}  # 请求参数
#     )
    
#     print('Headers:', headers)
#     """ 输出示例：
#     {
#         'X-Timestamp': '1730986454309',
#         'X-Nonce': 'a6a01407-f06f-451e-9d37-f9bdc4d7bc11',
#         'Content-Type': 'application/json',
#         'Authorization': 'ak_0f773...:5062004fc8...'
#     }
#     """