from collections.abc import Generator
from typing import Any
import httpx
import json
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

BASE_API_URL = "https://api-ai-oracle.apro.com"
class TickerCurrencyPriceTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        params = {
            "name": tool_parameters.get("name", ""),
            "quotation": tool_parameters.get("quotation", ""),
            "type": tool_parameters.get("type", ""),
        }
        if not params["name"]:
            yield self.create_text_message("Please input name")
        if not params["quotation"]:
            yield self.create_text_message("Please input quotation")

        try:
            res = httpx.get(BASE_API_URL+"/v1/ticker/currency/price", params=params)
            if res.status_code == 200:
                response = res.json()
                if response["status"]["code"] != 200:
                    yield self.create_text_message(
                        f"Failed to get ticker currency price, status code: {response["status"]["code"]}, response: {response["status"]}"
                    )
                else:
                    text_message = self.create_text_message(json.dumps(response["data"], indent=None, ensure_ascii=False))
                    json_message =  self.create_json_message(response["data"])
                    yield from [json_message, text_message]
            else:
                yield self.create_text_message(
                    f"Failed to get ticker currency price, status code: {res.status_code}"
                )
        except Exception as e:
            yield self.create_text_message(
                "Failed to send message to APRO ai oracle. {}".format(e)
            )
