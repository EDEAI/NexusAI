from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.base import WaterCrawlBaseMixin


class ScrapeTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        include_html = tool_parameters.get("include_html", False)
        make_screenshot = tool_parameters.get("make_screenshot", False)
        return_json = tool_parameters.get("return_json", False)
        include_links = tool_parameters.get("include_links", False)
        timeout = tool_parameters.get("timeout", 15000)
        wait_time = tool_parameters.get("wait_time", 1000)
        actions = []

        if make_screenshot:
            actions.append({
                'type': 'screenshot',
            })

        response = self.client.scrape_url(
            url=tool_parameters["url"],
            download=True,
            page_options={
                'include_html': include_html,
                'include_links': include_links,
                'timeout': timeout,
                'wait_time': wait_time,
                'actions': actions
            }
        )

        if not response:
            yield self.create_text_message(
                'No result found for the given URL'
            )
            return

        if return_json:
            yield self.create_json_message(
                response
            )

        result = response.pop('result')
        markdown = result.get('markdown')
        html = result.get('html')

        yield self.create_variable_message(
            'markdown', markdown or ''
        )

        if include_html:
            yield self.create_variable_message(
                'html', html or ''
            )

        if include_links:
            yield self.create_variable_message(
                'links', result.get('links') or []
            )

        if make_screenshot:
            for attachment in response['attachments']:
                yield self.create_image_message(
                    attachment['attachment']
                )
