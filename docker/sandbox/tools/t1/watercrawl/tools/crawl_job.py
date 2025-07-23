from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool
from requests import HTTPError

from tools.base import WaterCrawlBaseMixin


class CrawlJobTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        operation = tool_parameters.get("operation", "get")
        try:
            crawl_request = self.client.get_crawl_request(tool_parameters["crawl_request_uuid"])
        except HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message("Crawl request not found")
                return
            raise e

        if operation == "get":
            yield self.create_json_message(crawl_request)
            return

        if operation == "cancel":
            yield from self.cancel_crawl_request(crawl_request)
            return

        if operation == "get_results":
            yield from self.get_crawl_results(crawl_request)
            return

        raise ValueError(f"Invalid operation: {operation}")

    def cancel_crawl_request(self, crawl_request: dict[str, Any]):
        try:
            self.client.stop_crawl_request(crawl_request["uuid"])
            yield self.create_text_message("Crawl request has been canceled")
        except HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message("Crawl request not found")
                return
            raise e

    def get_crawl_results(self, crawl_request: dict[str, Any]):
        if crawl_request['status'] not in ['finished', 'failed', 'canceled']:
            yield self.create_text_message("Crawl request is not stopped or finished")
            return

        crawl_request['results'] = []
        page = 1
        while True:
            response = self.client.get_crawl_request_results(crawl_request["uuid"], page=page)
            for result in response['results']:
                # Download the result from the server
                crawl_request['results'].append(self.client.download_result(result))

            if not response['next']:
                break
            page += 1

        yield self.create_json_message(crawl_request)
