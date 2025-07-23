from collections.abc import Generator
from typing import Any

from utils.cloudflare_d1 import cloudflare_d1_query, cloudflare_d1_result_success

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class DataConnectorCloudflareD1Tool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        account_id = self.runtime.credentials["cloudflare_account_id"]
        api_token = self.runtime.credentials["cloudflare_api_token"]
        database_id = tool_parameters["database_id"]
        sql_query = tool_parameters["query"]

        result = cloudflare_d1_query(account_id, database_id, api_token, sql_query, "")
        if "error" in result:
            error_message = f"Cloudflare D1 Query Error: {result['error']}. "
            if "metadata" in result:
                metadata = result["metadata"]
                error_message += "Details: "
                if "http_status" in metadata:
                    error_message += f"HTTP Status: {metadata['http_status']}, "
                if "detail" in metadata:
                    error_message += f"Detail: {metadata['detail']}, "
                if "response_payload" in metadata:
                    error_message += f"Response Payload: {metadata['response_payload']}"
                if "details" in metadata:  # For cloudflare_d1_error original structure
                    error_message += f"D1 Error Details: {metadata['details']}"
                if (
                    "raw_response" in metadata
                ):  # For cloudflare_d1_error original structure
                    error_message += f"Raw Response: {metadata['raw_response']}"

            # Raise exception if there's an error
            raise Exception(error_message)

        yield self.create_json_message(result)
        success = "True" if cloudflare_d1_result_success(result) else "False"
        yield self.create_text_message(success)
