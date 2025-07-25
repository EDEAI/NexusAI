from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from requests import HTTPError

from tools.base import WaterCrawlBaseMixin


class SearchJobTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        operation = tool_parameters.get("operation", "get")
        try:
            search_request = self.client.get_search_request(
                tool_parameters["search_request_uuid"], 
                download=True
            )
        except HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message("Search request not found")
                return
            raise e
        
        if operation == "get":
            yield self.create_json_message(search_request)
            return
        
        if operation == "cancel":
            yield from self.cancel_search_request(search_request)
            return
        
        if operation == "monitor":
            yield from self.monitor_search_request(search_request)
            return
        
        raise ValueError(f"Invalid operation: {operation}")
    
    def cancel_search_request(self, search_request: dict[str, Any]):
        try:
            self.client.stop_search_request(search_request["uuid"])
            yield self.create_text_message("Search request has been canceled")
        except HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message("Search request not found")
                return
            raise e
    
    def monitor_search_request(self, search_request: dict[str, Any]):
        if search_request['status'] in ['finished', 'failed', 'cancelled']:
            # If already completed, just return the results
            yield self.create_json_message(search_request)
            return
        
        # Monitor the search request in real-time
        for event in self.client.monitor_search_request(
            item_id=search_request['uuid'],
            download=True
        ):
            if event['type'] == 'state' and event['data']['status'] in ["finished", "failed"]:
                search_request = event['data']
                break
        
        yield self.create_json_message(search_request)
