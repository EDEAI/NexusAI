from typing import Any, Generator
import requests
import json
from pydantic import BaseModel, Field
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin import Tool


class FetchAnsByStackExQuesIDInput(BaseModel):
    id: int = Field(..., description="The question ID")
    site: str = Field(..., description="The Stack Exchange site")
    order: str = Field(..., description="asc or desc")
    sort: str = Field(..., description="activity, votes, creation")
    pagesize: int = Field(..., description="Number of answers per page")
    page: int = Field(..., description="Page number")


class FetchAnsByStackExQuesIDTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        input = FetchAnsByStackExQuesIDInput(**tool_parameters)
        params = {
            "site": input.site,
            "filter": "!nNPvSNdWme",
            "order": input.order,
            "sort": input.sort,
            "pagesize": input.pagesize,
            "page": input.page,
        }
        response = requests.get(f"https://api.stackexchange.com/2.3/questions/{input.id}/answers", params=params)
        if response.status_code == 200:
            # self.session.model.summary.invoke(user_id=self.runtime.user_id, content=response.text)
            yield self.create_json_message(json.loads(response.text))
        else:
            yield self.create_text_message(f"API request failed with status code {response.status_code}")
