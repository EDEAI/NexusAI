from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from requests import HTTPError

from tools.base import WaterCrawlBaseMixin


class SitemapTool(WaterCrawlBaseMixin, Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        sitemap_type = tool_parameters.get("sitemap_type", "default")
        crawl_request_uuid = tool_parameters.get("crawl_request_uuid")
        
        if not crawl_request_uuid:
            yield self.create_text_message("Crawl request UUID is required")
            return
        
        try:
            # Fetch the crawl request to verify it exists
            crawl_request = self.client.get_crawl_request(crawl_request_uuid)
        except HTTPError as e:
            if e.response.status_code == 404:
                yield self.create_text_message("Crawl request not found")
                return
            raise e
        
        # Check if the crawl request has a sitemap
        if 'sitemap' not in crawl_request or not crawl_request['sitemap']:
            yield self.create_text_message("Sitemap not found in this crawl request")
            return
        
        try:
            if sitemap_type == "default":
                # Download the regular sitemap
                sitemap_data = self.client.download_sitemap(crawl_request)
                yield self.create_json_message(sitemap_data)
                
            elif sitemap_type == "graph":
                # Download the sitemap as a graph representation
                graph_data = self.client.download_sitemap_graph(crawl_request)
                yield self.create_json_message(graph_data)
                
            elif sitemap_type == "markdown":
                # Download the sitemap as markdown
                markdown_content = self.client.download_sitemap_markdown(crawl_request)
                yield self.create_text_message(markdown_content)
            
            else:
                yield self.create_text_message(f"Invalid sitemap type: {sitemap_type}. "
                                              f"Valid types are: default, graph, markdown")
                
        except HTTPError as e:
            if 400 <= e.response.status_code < 500:
                yield self.create_json_message({
                    'status_code': e.response.status_code,
                    'response': e.response.json()
                })
                return
            raise e
        except ValueError as e:
            yield self.create_text_message(str(e))
            return
