from pathlib import Path

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

from core.database.models import AIToolLLMRecords, AppRuns, Models
from core.llm import LLMPipeline, Messages

project_root = Path(__file__).absolute().parent.parent.parent
ai_tool_llm_records = AIToolLLMRecords()
app_runs = AppRuns()

async def call_llm_for_ai_tool(
    team_id: int,
    user_id: int,
    app_run_id: int,
    input_messages: Messages,
    return_json: bool = False
) -> str:
    model_info = Models().get_model_by_type(1, team_id, uid=user_id)
    llm_config = {**model_info['supplier_config'], **model_info['model_config']}
    if return_json:
        llm_config['model_kwargs'] = {'response_format': {'type': 'json_object'}}
    llm_pipeline = LLMPipeline(supplier=model_info['supplier_name'], config=llm_config)
    input_ = [(role, message.value) for role, message in input_messages.messages]

    # Request LLM
    result = await llm_pipeline.llm.agenerate([input_])
    result: ChatGeneration = result.generations[0][0]
    output_message: AIMessage = result.message

    # LLM output & token usage recording
    if usage_metadata := output_message.usage_metadata:
        prompt_tokens = usage_metadata['input_tokens']
        completion_tokens = usage_metadata['output_tokens']
        total_tokens = usage_metadata['total_tokens']
    ai_tool_llm_records.insert(
        {
            'app_run_id': app_run_id,
            'llm_input': input_,
            'message': output_message.content,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens
        }
    )
    app_runs.increment_token_usage(
        app_run_id,
        prompt_tokens, completion_tokens, total_tokens
    )
    return output_message.content