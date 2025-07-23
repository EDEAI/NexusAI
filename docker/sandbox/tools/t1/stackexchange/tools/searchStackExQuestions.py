from typing import Any, Generator
import requests
import json
from pydantic import BaseModel, Field
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class SearchStackExQuestionsInput(BaseModel):
    intitle: str = Field(..., description="The search query.")
    sort: str = Field(..., description="The sort order - relevance, activity, votes, creation.")
    order: str = Field(..., description="asc or desc")
    site: str = Field(..., description="The Stack Exchange site.")
    tagged: str = Field(None, description="Semicolon-separated tags to include.")
    nottagged: str = Field(None, description="Semicolon-separated tags to exclude.")
    accepted: bool = Field(..., description="true for only accepted answers, false otherwise")
    pagesize: int = Field(..., description="Number of results per page")


class SearchStackExQuestionsTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        input = SearchStackExQuestionsInput(**tool_parameters)
        params = {
            "intitle": input.intitle,
            "sort": input.sort,
            "order": input.order,
            "site": input.site,
            "accepted": input.accepted,
            "pagesize": input.pagesize,
        }
        if input.tagged:
            params["tagged"] = input.tagged
        if input.nottagged:
            params["nottagged"] = input.nottagged
        response = requests.get("https://api.stackexchange.com/2.3/search", params=params)
        if response.status_code == 200:
            yield self.create_json_message(json.loads(response.text))
        else:
            yield self.create_text_message(f"API request failed with status code {response.status_code}")
