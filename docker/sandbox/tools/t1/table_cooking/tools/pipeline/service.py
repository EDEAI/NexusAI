import io
from typing import Any, NoReturn
from urllib.parse import urlparse

import pandas as pd
import tiktoken
from dify_plugin.core.runtime import Session
from dify_plugin.entities.model.llm import LLMModelConfig
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.file.file import File
from loguru import logger
from pydantic import BaseModel

from tools.ai.table_self_query import TableQueryEngine, QueryResult

WRAPPER_HUMAN_READY = """
### Query code

```python
{py_code}
```

### Preview of execution results

{result_markdown}
"""

WRAPPER_LLM_READY = """
```xml
<segment table="{table_name}">
<question>{question}</question>
<code>
{query_code}
</code>
<output filename="{recommend_filename}">
{result_markdown}
</output>
</segment>
```
"""

encoding = tiktoken.get_encoding("o200k_base")


class ArtifactPayload(BaseModel):
    natural_query: str
    """
    Natural language query description.
    Todo: In multiple rounds of dialogue, this should be a semantic complete query after being spliced by the memory model.
    """

    table: File
    """
    Dify table
    """

    dify_model_config: LLMModelConfig
    """
    Dify LLM model configuration
    """

    enable_classifier: bool = True
    """
    Start the problem classifier and let the query flow to `simple query` or `complex calculation`
    """

    def get_table_stream(self) -> io.BytesIO:
        return io.BytesIO(self.table.blob)

    @staticmethod
    def validation(tool_parameters: dict[str, Any]) -> NoReturn | None:
        query = tool_parameters.get("query")
        table = tool_parameters.get("table")
        chef = tool_parameters.get("chef")

        # !!<LLM edit>
        if not query or not isinstance(query, str):
            raise ToolProviderCredentialValidationError("Query is required and must be a string.")
        if not table or not isinstance(table, File):
            raise ToolProviderCredentialValidationError("Table is required and must be a file.")
        if table.extension not in [".csv", ".xls", ".xlsx"]:
            raise ToolProviderCredentialValidationError("Table must be a csv, xls, or xlsx file.")

        # Check if the URL is of string type
        if not isinstance(table.url, str):
            raise ToolProviderCredentialValidationError("URL must be a string.")

        # Parses URL and verify scheme
        parsed_url = urlparse(table.url)
        if parsed_url.scheme not in ["http", "https"]:
            scheme = parsed_url.scheme or "missing"
            raise ToolProviderCredentialValidationError(
                f"Invalid URL scheme '{scheme}'. FILES_URL must start with 'http://' or 'https://'."
                f"Please check more details https://github.com/langgenius/dify/blob/72191f5b13c55b44bcd3b25f7480804259e53495/docker/.env.example#L42"
            )
        # !!</LLM edit>

        # Prevent stupidity
        not_available_models = [
            "gpt-4.5-preview",
            "gpt-4.5-preview-2025-02-27",
            "o1",
            "o1-2024-12-17",
            "o1-pro",
            "o1-pro-2025-03-19",
        ]
        if (
            isinstance(chef, dict)
            and chef.get("model_type", "") == "llm"
            and chef.get("provider", "") == "langgenius/openai/openai"
            and chef.get("mode", "") == "chat"
        ):
            if use_model := chef.get("model"):
                if use_model in not_available_models:
                    raise ToolProviderCredentialValidationError(
                        f"Model `{use_model}` is not available for this tool. "
                        f"Please replace other cheaper models."
                    )

    @classmethod
    def from_dify(cls, tool_parameters: dict[str, Any], *, enable_classifier: bool = True):
        query = tool_parameters.get("query")
        table = tool_parameters.get("table")
        dify_model_config = tool_parameters.get("chef")

        ArtifactPayload.validation(tool_parameters)

        return cls(
            natural_query=query,
            dify_model_config=dify_model_config,
            table=table,
            enable_classifier=enable_classifier,
        )


class CodeInterpreter(BaseModel):
    code: str


class CookingResultParams(BaseModel):
    code: str
    natural_query: str
    recommend_filename: str
    input_tokens: int
    input_table_name: str


class CookingResult(BaseModel):
    llm_ready: str
    human_ready: str
    params: CookingResultParams


def transform_friendly_prompt_template(
    question: str, table_name: str, query_code: str, recommend_filename: str, result_data: Any
):
    preview_df = pd.DataFrame.from_records(result_data)
    result_markdown = preview_df.to_markdown(index=False)

    human_ready = WRAPPER_HUMAN_READY.format(py_code=query_code, result_markdown=result_markdown)

    llm_ready = WRAPPER_LLM_READY.format(
        question=question,
        table_name=table_name,
        query_code=query_code,
        recommend_filename=recommend_filename,
        result_markdown=result_markdown,
    ).strip()

    return llm_ready, human_ready


@logger.catch
def table_self_query(artifact: ArtifactPayload, session: Session) -> CookingResult | None:
    engine = TableQueryEngine(session=session, dify_model_config=artifact.dify_model_config)
    engine.load_table(file_stream=artifact.get_table_stream(), extension=artifact.table.extension)

    result: QueryResult = engine.query(artifact.natural_query)
    if not result:
        return

    if result.error:
        logger.error(result.error)

    recommend_filename = result.get_recommend_filename(suffix=".md")

    # ====================================================
    # Convert answer to XML format content of LLM_READY
    # ====================================================
    # Since the query result data volume may be very large,
    # it is not advisable to insert the complete content into the session polluting context.
    # The best practice is to insert preview lines and resource preview links
    __xml_context__, __preview_context__ = transform_friendly_prompt_template(
        question=artifact.natural_query,
        table_name=artifact.table.filename,
        query_code=result.query_code,
        recommend_filename=recommend_filename,
        result_data=result.data,
    )

    # ==========================================================================
    # Excessively long text should be printed directly instead of output by LLM
    # ==========================================================================
    input_tokens = len(encoding.encode(__xml_context__))

    # ==========================================================================
    # todo: Return to the table preview file after operation
    # ==========================================================================

    return CookingResult(
        llm_ready=__xml_context__,
        human_ready=__preview_context__,
        params=CookingResultParams(
            code=result.query_code,
            natural_query=artifact.natural_query,
            recommend_filename=recommend_filename,
            input_tokens=input_tokens,
            input_table_name=artifact.table.filename,
        ),
    )
