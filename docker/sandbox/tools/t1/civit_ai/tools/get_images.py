from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .civitai_client import CivitAI


class GetImages(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        api_key = self.runtime.credentials.get("civitai_api_key")
        if not api_key:
            yield self.create_text_message("Please input api_key")
        cli = CivitAI(api_key)
        json = cli.get_images(limit=tool_parameters.get("limit", 20),
                              postId=tool_parameters.get("postId"),
                              modelId=tool_parameters.get("modelId"),
                              modelVersionId=tool_parameters.get(
                                  "modelVersionId"),
                              username=tool_parameters.get("username"),
                              nsfw=tool_parameters.get("nsfw"),
                              sort=tool_parameters.get("sort"),
                              period=tool_parameters.get("period"),
                              page=tool_parameters.get("page"))
        yield self.create_json_message(json)

        mapping = {"id": [item["id"] for item in json["items"]],
                   "url": [item["url"] for item in json["items"]],
                   "hash": [item["hash"] for item in json["items"]],
                   "width": [item["width"] for item in json["items"]],
                   "height": [item["height"] for item in json["items"]],
                   "nsfw": [item["nsfw"] for item in json["items"]],
                   "nsfwLevel": [item["nsfwLevel"] for item in json["items"]],
                   "postId": [item["postId"] for item in json["items"]],
                   "cryCount": [item["stats"]["cryCount"] for item in json["items"]],
                   "laughCount": [item["stats"]["laughCount"] for item in json["items"]],
                   "likeCount": [item["stats"]["likeCount"] for item in json["items"]],
                   "heartCount": [item["stats"]["heartCount"] for item in json["items"]],
                   "commentCount": [item["stats"]["commentCount"] for item in json["items"]],
                   "username": [item["username"] for item in json["items"]],
                   "nextCursor": [item.get("nextCursor", -1) for item in json["items"]],
                   "currentPage": [item.get("currentPage", -1) for item in json["items"]],
                   "pageSize": [item.get("pageSize", -1) for item in json["items"]],
                   "nextPage": [item.get("nextPage", "") for item in json["items"]], }
        for key in mapping:
            yield self.create_variable_message(key, mapping[key])
