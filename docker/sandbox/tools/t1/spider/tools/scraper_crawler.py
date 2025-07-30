from typing import Any, Generator
from dify_plugin.entities.tool import ToolInvokeMessage
from spiderApp import RequestParamsDict, Spider
from dify_plugin import Tool


class ScrapeTool(Tool):
    def _invoke(
        self,  tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app = Spider(api_key=self.runtime.credentials["spider_api_key"])
        url = tool_parameters["url"]
        mode = tool_parameters["mode"]
        options:RequestParamsDict ={
            "limit": tool_parameters.get("limit", 0),
            "depth": tool_parameters.get("depth", 0),
            "readability": tool_parameters.get("readability", False),
        }
        result = ""
        try:
            if mode == "scrape":
                scrape_result = app.scrape_url(url=url, params=options)
                for i in scrape_result:
                    result += "URL: " + i.get("url", "") + "\n"
                    result += "CONTENT: " + i.get("content", "") + "\n\n"
            elif mode == "crawl":
                crawl_result = app.crawl_url(url=tool_parameters["url"], params=options)
                for i in crawl_result:
                    result += "URL: " + i.get("url", "") + "\n"
                    result += "CONTENT: " + i.get("content", "") + "\n\n"
        except Exception as e:
            yield self.create_text_message("An error occurred", str(e))
        yield self.create_text_message(result)
