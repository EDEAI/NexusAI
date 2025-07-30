import json
from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from requests import HTTPError

from tools.base import WaterCrawlBaseMixin


class CrawlTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        wait_for_results = tool_parameters.get('wait_for_results', True)
        extra_headers = {}
        if tool_parameters.get('headers'):
            try:
                extra_headers = json.loads(tool_parameters['headers'])
            except json.JSONDecodeError:
                yield self.create_text_message(
                    'Invalid headers provided. Please provide a valid JSON object.'
                )
                return

        try:
            crawl_request = self.client.create_crawl_request(
                url=tool_parameters["url"],
                spider_options={
                    'allowed_domains': self.get_safe_array(tool_parameters, 'allowed_domains'),
                    'max_depth': tool_parameters.get('max_depth', 1),
                    'page_limit': tool_parameters.get('page_limit', 1),
                    'exclude_paths': self.get_safe_array(tool_parameters, 'exclude_paths'),
                    'include_paths': self.get_safe_array(tool_parameters, 'include_paths'),
                },
                page_options={
                    'exclude_tags': self.get_safe_array(tool_parameters, 'exclude_tags'),
                    'include_tags': self.get_safe_array(tool_parameters, 'include_tags'),
                    'wait_time': tool_parameters.get('wait_time', 1000),
                    'only_main_content': tool_parameters.get('only_main_content', True),
                    'include_html': tool_parameters.get('include_html', False),
                    'include_links': tool_parameters.get('include_links', False),
                    'timeout': tool_parameters.get('timeout', 3000),
                    'locale': tool_parameters.get('locale', 'en-US'),
                    'extra_headers': extra_headers,
                    'actions': [],
                }
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

        if not wait_for_results:
            yield self.create_json_message(
                crawl_request
            )
            return

        crawl_request['results'] = []
        for result in self.client.monitor_crawl_request(
            item_id=crawl_request['uuid'],
            download=True
        ):
            if result['type'] == 'result':
                crawl_request['results'].append(result['data'])

        yield self.create_json_message(
            crawl_request
        )
        
