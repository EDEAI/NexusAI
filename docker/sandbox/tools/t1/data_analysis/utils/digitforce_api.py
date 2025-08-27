"""
digitforce api
"""
import json
import requests

class DigitForceApi():
    def __init__(self, api_key):
        self.api_key = api_key

    def get_header_url(self, service_name,type="prod"):
        if type == "prod":
            api_base = "https://prod.digitforce.com/api/aigc/v1/dify/"
            headers = {
                "Authorization": self.api_key,
            }
        elif type == "testdemo":
            api_base = "http://10.10.20.29:8905/api/aigc/v1/dify/"
            headers = {
                "Cookie": f"access-token={self.api_key}",
            }
        elif type == "test":
            api_base = "http://172.22.20.63:8904/api/aigc/v1/dify/"
            headers = {
                "Cookie": f"access-token={self.api_key}",
            }
        elif type == "localhost":
            api_base = "http://localhost:8910/api/aigc/v1/dify/"
            headers = {
                "Cookie": f"access-token={self.api_key}",
            }
        url = api_base + service_name
        return headers, url

    def dify_api_post(self, data: dict, service_name: str):
        headers, url = self.get_header_url(service_name, type="prod")
        headers["X-Platform-Source"] = "dify"
        # 增加版本号
        data['version'] = "1.0.12"
        response = requests.post(url, headers=headers, data=json.dumps(data)).json()
        if response.get("status") != 200:
            raise Exception(
                f"response error: {response}"
            )
        return response.get("data")
