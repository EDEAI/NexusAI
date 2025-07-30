from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.pipeline.service import ArtifactPayload, table_self_query


class TableCookingTool(Tool):
    """
    Invoke model:
    https://docs.dify.ai/zh-hans/plugins/schema-definition/reverse-invocation-of-the-dify-service/model#zui-jia-shi-jian
    """

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # Parameter verification
        ArtifactPayload.validation(tool_parameters)

        # Build artifact for QA
        artifact = ArtifactPayload.from_dify(tool_parameters)

        # Invoke tool-strategy
        cooking_result = table_self_query(artifact, self.session)
        if cooking_result:
            cooking_result_json = cooking_result.model_dump(mode="json")
            yield self.create_text_message(cooking_result.human_ready)
            yield self.create_json_message(cooking_result_json)
        else:
            yield self.create_text_message(
                "Sorry, I can't generate a SQL statement for your query."
            )
