from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from requests import HTTPError

from tools.base import WaterCrawlBaseMixin


class SearchTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        wait_for_results = tool_parameters.get('wait_for_results', True)
        result_limit = tool_parameters.get('result_limit', 5)
        
        search_options = {
            'language': tool_parameters.get('language'),
            'country': tool_parameters.get('country'),
            'time_range': tool_parameters.get('time_range', 'any'),
            'search_type': tool_parameters.get('search_type', 'web'),
            'depth': tool_parameters.get('depth', 'basic')
        }
        
        # Remove None values
        search_options = {k: v for k, v in search_options.items() if v}
        
        try:
            search_request = self.client.create_search_request(
                query=tool_parameters["query"],
                search_options=search_options,
                result_limit=result_limit,
                sync=wait_for_results,
                download=True
            )
        except HTTPError as e:
            if 400 <= e.response.status_code < 500:
                yield self.create_json_message(
                    {
                        'status_code': e.response.status_code,
                        'response': e.response.json()
                    }
                )
                return
            
            raise e
        
        yield self.create_json_message(
            search_request
        )

