from collections.abc import Generator
from typing import Any, Literal
from faker import Faker
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
import csv
import json
from io import StringIO


class FakerTool(Tool):
    
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        """
        生成假数据，同时返回文本、JSON和CSV三种格式
        """
        # 获取参数
        locale = tool_parameters.get("locale") or "en_US"
        data_type = tool_parameters.get("type") or "name"
        count = min(max(tool_parameters.get("count", 1), 1), 1000)

        # 初始化 Faker
        fake = Faker(locale)
        results = []

        # 生成数据
        for _ in range(count):
            match data_type:
                case "name":
                    results.append(fake.name())
                case "address":
                    results.append(fake.address())
                case "phone_number":
                    results.append(fake.phone_number())
                case "email":
                    results.append(fake.email())
                case "credit_card_number":
                    results.append(fake.credit_card_number())
                case _:
                    yield self.create_text_message(f"❌ Unsupported type: {data_type}")
                    return

        # 返回文本格式
        text_content = "\n".join(results)
        yield self.create_text_message(text_content)

        # 返回 JSON 格式
        json_content = json.dumps({"results": results}, ensure_ascii=False)
        yield self.create_blob_message(
            blob=json_content,
            meta={"mime_type": "application/json"}
        )

        # 返回 CSV 格式
        csv_output = self._convert_to_csv(results)
        yield self.create_blob_message(
            blob=csv_output,
            meta={"mime_type": "text/csv"}
        )


    def _convert_to_csv(self, data: list) -> str:
        """
        将数据转换为 CSV 格式字符串
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # 处理结构化数据
        if isinstance(data[0], dict):
            writer.writerow(data[0].keys())
            for item in data:
                writer.writerow(item.values())
        else:
            writer.writerow(["Data"])
            for item in data:
                writer.writerow([item])

        return output.getvalue()
