import asyncio

from fastapi import APIRouter, Request
from api.utils.common import *
from api.utils.jwt import *
from api.schema.agent import *
from api.schema.base import *
from core.database.models.agents import Agents
from core.database.models.apps import Apps
from core.database.models.app_runs import AppRuns
from core.database.models.agent_abilities import AgentAbilities
from core.database.models.agent_chat_messages import AgentChatMessages
from core.workflow.nodes import AgentNode
from core.workflow.variables import create_variable_from_dict
from core.llm.prompt import create_prompt_from_dict, Prompt
from core.llm.messages import Messages
from celery_app import run_app
from languages import get_language_content
from time import time
import json
from core.database.models.ai_tool_llm_records import AIToolLLMRecords
import traceback
from core.database.models.models import Models
from core.helper import truncate_messages_by_token_limit
from core.database.models.chatrooms import Chatrooms  # add import if not present

router = APIRouter()


@router.get("/agent_list", response_model=ResAgentListSchema)
async def agent_list(page: int = 1, page_size: int = 10, agent_search_type: int = 1, name: str = "",
                     userinfo: TokenData = Depends(get_current_user)):
    """
    agent list

    page: int, page number.
    page_size: int, quantity per page.
    agent_search_type: int, agent search type 1: my agent 2: team agent 3: select my agent.
    name: str, app and agent name.
    """
    agents_model = Agents()
    result = agents_model.get_agent_list(page, page_size, userinfo.uid, userinfo.team_id, agent_search_type, name)

    return response_success(result, get_language_content("api_agent_success"))


@router.put("/agent_base_update/{agent_id}", response_model=ResAgentBaseCreateSchema)
async def agent_base_update(request: Request, agent_id: int, data: ReqAgentBaseCreateSchema,
                            userinfo: TokenData = Depends(get_current_user)):
    """
    agent base update

    agent_id: int, Agent id
    is_public: int, Is it open to team members? 0: No 1: Yes
    attrs_are_visible: int, Are attributes of this app visible? 0: No 1: Yes
    enable_api: int, Whether to enable API 0: No 1: Yes
    obligations: str, Agent obligations
    input_variables: dict, Input variables
    dataset_ids: list, Multiple dataset id
    m_config_id: int, Model configuration ID
    allow_upload_file: int, Is it allowed to upload files? 0: No 1: Yes
    default_output_format: int, Default output format 1: text 2: json 3: code
    """

    update_data = data.dict(exclude_unset=True)
    is_public = data.is_public
    attrs_are_visible = data.attrs_are_visible
    enable_api = data.enable_api
    obligations = data.obligations
    input_variables = data.input_variables
    dataset_ids = data.dataset_ids
    m_config_id = data.m_config_id
    allow_upload_file = data.allow_upload_file
    default_output_format = data.default_output_format

    if agent_id <= 0:
        return response_error(get_language_content("api_agent_base_update_agent_id_required"))
    if is_public not in [0, 1]:
        return response_error(get_language_content("api_agent_base_update_is_public_error"))
    if 'attrs_are_visible' in update_data and attrs_are_visible not in [0, 1]:
        return response_error(get_language_content("api_agent_base_update_attrs_are_visible_error"))
    if 'attrs_are_visible' not in update_data:
        attrs_are_visible = 1
    if enable_api not in [0, 1]:
        return response_error(get_language_content("api_agent_base_update_enable_api_error"))
    if input_variables:
        try:
            create_variable_from_dict(input_variables)
        except:
            return response_error(get_language_content("api_agent_base_update_input_variables_wrong"))
    if m_config_id <= 0:
        return response_error(get_language_content("api_agent_base_update_m_config_id_required"))
    if allow_upload_file not in [0, 1]:
        return response_error(get_language_content("api_agent_base_update_allow_upload_file_error"))
    if default_output_format not in [1, 2, 3]:
        return response_error(get_language_content("api_agent_base_update_default_output_format_error"))

    agents_model = Agents()
    result = agents_model.agent_base_update(agent_id, userinfo.uid, userinfo.team_id, is_public, enable_api,
                                            obligations, input_variables, dataset_ids, m_config_id, allow_upload_file,
                                            default_output_format, attrs_are_visible)
    if result["status"] != 1:
        return response_error(result["message"])
    app_id = result["data"]["app_id"]

    return response_success(result["data"], get_language_content("api_agent_success"))


@router.put("/agent_abilities_set/{agent_id}", response_model=RespBaseSchema)
async def agent_abilities_set(agent_id: int, data: ReqAgentAbilitiesSetSchema,
                              userinfo: TokenData = Depends(get_current_user)):
    """
    agent abilities set

    agent_id: int, Agent id
    auto_match_ability: int, Whether to automatically match abilities 0: No 1: Yes
    agent_abilities: list, Agent abilities list
    agent_abilities.agent_ability_id: int, Agent abilities id
    agent_abilities.name: str, Ability name
    agent_abilities.content: str, Ability content
    agent_abilities.status: int, Ability status 1: Normal 2: Disabled
    agent_abilities.output_format: int, Output format 0: defalut 1: text 2: json 3: code
    """
    auto_match_ability = data.auto_match_ability
    agent_abilities = data.agent_abilities

    if agent_id <= 0:
        return response_error(get_language_content("api_agent_abilities_set_agent_id_required"))
    if auto_match_ability not in [0, 1]:
        return response_error(get_language_content("api_agent_abilities_set_auto_match_ability_error"))

    agents_model = Agents()
    result = agents_model.agent_abilities_set(agent_id, userinfo.uid, auto_match_ability, agent_abilities)
    if result["status"] != 1:
        return response_error(result["message"])

    return response_success(result["data"], get_language_content("api_agent_success"))


@router.put("/agent_publish/{agent_id}", response_model=RespBaseSchema)
async def agent_publish(request: Request, agent_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    agent publish

    agent_id: int, Agent id
    """
    if agent_id <= 0:
        return response_error(get_language_content("api_agent_publish_agent_id_required"))

    # Agent validation
    agents_model = Agents()
    agent = agents_model.get_agent_by_id(agent_id)
    app_id = agent['app_id']
    app = Apps().get_app_by_id(app_id)
    node = AgentNode(
        title=app['name'],
        desc=app['description'],
        input=create_variable_from_dict(agent['input_variables']),
        agent_id=agent_id,
        ability_id=0,
        prompt=Prompt(),
    )
    try:
        node.validate()
    except Exception as e:
        return response_error(str(e))

    result = agents_model.agent_publish(agent_id, userinfo.uid)
    if result["status"] != 1:
        return response_error(result["message"])

    return response_success(result["data"], get_language_content("api_agent_success"))


@router.delete("/agent_delete/{app_id}", response_model=RespBaseSchema)
async def agent_delete(request: Request, app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    agent delete

    app_id: int, App id
    """
    if app_id <= 0:
        return response_error(get_language_content("api_agent_delete_app_id_required"))

    agents_model = Agents()
    result = agents_model.agent_delete(app_id, userinfo.uid)
    if result["status"] != 1:
        return response_error(result["message"])

    return response_success(result["data"], get_language_content("api_agent_success"))


@router.get("/agent_info/{app_id}", response_model=ResAgentInfoSchemaUpdate)
async def agent_info(app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
    # ResAgentInfoSchema
    agent info

    app_id: int, App id
    publish_status: int, Agent publish status 0: Draft 1: Published
    """
    if app_id <= 0:
        return response_error(get_language_content("api_agent_info_app_id_required"))
    if publish_status not in [0, 1]:
        return response_error(get_language_content("api_agent_info_publish_status_error"))

    agents_model = Agents()
    result = agents_model.agent_info(app_id, publish_status, userinfo.uid, userinfo.team_id)
    if result["status"] != 1:
        return response_error(result["message"])

    return response_success(result["data"], get_language_content("api_agent_success"))


@router.post("/agent_run", response_model=ResAgentRunSchema)
async def agent_run(data: ReqAgentRunSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    agent run

    agent_id: int, Agent id
    ability_id: int, Ability id
    input_dict: dict, Input data
    prompt: dict, Prompt data
    """
    agent_id = data.agent_id
    ability_id = data.ability_id
    input_dict = data.input_dict
    prompt = data.prompt
    uid = userinfo.uid
    team_id = userinfo.team_id
    data_source_run_id = data.data_source_run_id

    if agent_id <= 0:
        return response_error(get_language_content("api_agent_run_agent_id_required"))
    if not input_dict:
        return response_error(get_language_content("api_agent_run_input_dict_required"))
    try:
        create_variable_from_dict(input_dict)
    except:
        return response_error(get_language_content("api_agent_run_input_dict_wrong"))
    if not prompt:
        return response_error(get_language_content("api_agent_run_prompt_required"))
    try:
        create_prompt_from_dict(prompt)
    except:
        return response_error(get_language_content("api_agent_run_prompt_wrong"))

    # get agent
    agents_model = Agents()
    agent = agents_model.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": agent_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]
    )
    if not agent:
        return response_error(get_language_content("api_agent_run_agent_error"))
    if agent["user_id"] != uid:
        if agent["status"] != 1:
            return response_error(get_language_content("api_agent_run_agent_status_not_normal"))
        if agent["publish_status"] != 1:
            return response_error(get_language_content("api_agent_run_not_creators"))

    # get app
    apps_model = Apps()
    app = apps_model.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": agent["app_id"]},
            {"column": "team_id", "value": team_id},
            {"column": "mode", "value": 1},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]
    )
    if not app:
        return response_error(get_language_content("api_agent_run_app_error"))
    if app["user_id"] != uid:
        if app["is_public"] == 0:
            return response_error(get_language_content("api_agent_run_team_not_open"))
        if app["status"] != 1:
            return response_error(get_language_content("api_agent_run_app_status_not_normal"))

    # get agent ability
    if ability_id != 0:
        agent_abilities_model = AgentAbilities()
        ability = agent_abilities_model.select_one(
            columns="*",
            conditions=[
                {"column": "id", "value": ability_id},
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not ability:
            return response_error(get_language_content("api_agent_run_ability_error"))
        if ability["user_id"] != uid and ability["status"] != 1:
            return response_error(get_language_content("api_agent_run_ability_status_not_normal"))

    task = run_app.delay(app_type="agent", id_=agent_id, user_id=uid, input_dict=input_dict, ability_id=ability_id,
                         prompt=prompt, data_source_run_id=data_source_run_id)
    while not task.ready():
        await asyncio.sleep(0.1)
    result = task.get()
    if result["status"] != "success":
        return response_error(result["message"])

    return response_success({"outputs": result["data"]["outputs"], "outputs_md": result["data"]["outputs_md"]},
                            get_language_content("api_agent_success"))


@router.post("/agent_generate", response_model=ResAgentGenerateSchema)
async def agent_generate(data: ReqAgentGenerateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Generate an agent based on user prompt

    Args:
        data (ReqAgentGenerateSchema): Request data containing:
            user_prompt (str): The prompt text used to generate the agent
        userinfo (TokenData): User authentication information

    Returns:
        JSON response containing:
            app_run_id (int): The ID of the app run
            record_id (int): The ID of the LLM record

    Raises:
        - Returns error if prompt is empty
        - Returns error if record creation fails
    """
    # Validate user prompt
    if not data.user_prompt:
        return response_error(get_language_content("api_agent_user_prompt_required"))

    try:
        # Create app run record
        start_datetime_str = datetime.fromtimestamp(time()) \
            .replace(microsecond=0).isoformat(sep='_')
        app_run_id = AppRuns().insert({
            'user_id': userinfo.uid,
            'app_id': 0,
            'type': 2,
            'name': f'Agent_Generator_{start_datetime_str}',
            'status': 1  # Initial status
        })

        # Prepare prompts for LLM
        system_prompt = get_language_content('generate_agent_system_prompt', userinfo.uid)
        user_prompt = get_language_content('generate_agent_user', userinfo.uid, False)

        user_prompt = user_prompt.format(
            user_prompt=data.user_prompt
        )

        system_prompt = system_prompt.format(
            append_prompt=''
        )
        input_ = Prompt(
            system=system_prompt,
            user=user_prompt
        ).to_dict()

        # Initialize LLM execution record
        record_id = AIToolLLMRecords().initialize_execution_record(
            app_run_id=app_run_id,
            ai_tool_type=1,  # Agent generator type
            inputs=input_,
            run_type=1,
            user_prompt=data.user_prompt
        )

        if not record_id:
            return response_error(get_language_content("api_agent_generate_failed"))

        # Return successful response
        return response_success(
            {
                "app_run_id": app_run_id,
                "record_id": record_id
            },
            get_language_content("api_agent_success")
        )

    except Exception as e:
        return response_error(get_language_content("api_agent_generate_failed"))


@router.post('/agent_regenerate', response_model=ResAgentGenerateSchema)
async def agent_regenerate(data: ReqAgentRegenerateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Regenerate an agent based on previous generation history

    Args:
        data (ReqAgentRegenerateSchema): Request data containing:
            app_run_id (int): The ID of the original app run
        userinfo (TokenData): User authentication information

    Returns:
        JSON response containing:
            app_run_id (int): The ID of the app run

    Raises:
        - Returns error if app_run_id is invalid
        - Returns error if record retrieval fails
    """
    # Validate app run exists and belongs to user
    app_run_info = AppRuns().select_one(
        columns=["id"],
        conditions=[
            {"column": "id", "value": data.app_run_id},
            {"column": "user_id", "value": userinfo.uid}
        ]
    )

    if not app_run_info:
        return response_error(get_language_content('app_run_error'))

    runing_record = AIToolLLMRecords().select_one(
            columns=['loop_id'],
            conditions=[
                {"column": "app_run_id", "value": data.app_run_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ],
            limit=1
        )
    if runing_record:
        # There are records that are being executed.
        return response_error(get_language_content("agent_batch_exist_runing_rocord"))




    # Get all LLM records for this app run
    record_list = AIToolLLMRecords().select(
        columns=['id', 'inputs', 'outputs'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ]
    )

    # Extract original system prompt from first record
    base_system_prompt = ""
    base_user_prompt = ""
    first_record = record_list[0]
    inputs = first_record.get('inputs', {})

    # Get system prompt value from inputs
    try:
        if isinstance(inputs, dict) and 'system' in inputs:
            system_dict = inputs['system']
            if isinstance(system_dict, dict) and 'value' in system_dict:
                base_system_prompt = system_dict['value']

        if isinstance(inputs, dict) and 'user' in inputs:
            user_dict = inputs['user']
            if isinstance(user_dict, dict) and 'value' in user_dict:
                base_user_prompt = user_dict['value']
    except Exception as e:
        base_system_prompt = ""
        base_user_prompt = ""

    # Collect history agent list from all records
    history_agent_list = []
    for record in record_list:
        try:
            # Add outputs directly as they are already in dictionary format
            if record.get('outputs'):
                history_agent_list.append(record['outputs'])
        except Exception as e:
            continue

    # Filter out None values
    history_agent_list = [agent for agent in history_agent_list if agent]

    # Get latest record for updating status
    latest_record = AIToolLLMRecords().select_one(
        columns=['id', 'inputs', 'outputs'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ],
        order_by='id DESC'
    )

    model_info = Models().get_model_by_type(1, userinfo.team_id, uid=userinfo.uid)
    model_config_id = model_info['model_config_id']
    model_info = Models().get_model_by_config_id(model_config_id)
    history_agent_list = truncate_messages_by_token_limit(history_agent_list, model_info)

    # Format user prompt with history agent list
    user_prompt = get_language_content('regenerate_agent_user', userinfo.uid, False)
    user_prompt = user_prompt.format(
        history_agent_list=history_agent_list
    )
    regenerate_agent_system = get_language_content('regenerate_agent_system', userinfo.uid, False)

    # Prepare input for LLM
    input_ = Prompt(system=base_system_prompt + regenerate_agent_system, user=base_user_prompt + user_prompt).to_dict()

    try:
        # Mark previous record as processed
        AIToolLLMRecords().update(
            {'column': 'id', 'value': latest_record['id']},
            {'correct_output': 1}
        )

        AppRuns().update(
            {'column': 'id', 'value': data.app_run_id},
            {'status': 1}
        )

        # Initialize new execution record
        record_id = AIToolLLMRecords().initialize_execution_record(
            app_run_id=data.app_run_id,
            ai_tool_type=1,
            inputs=input_,
            run_type=2
        )

        if not record_id:
            return response_error(get_language_content("api_agent_generate_failed"))

        return response_success(
            {
                'app_run_id': data.app_run_id,
                'record_id': record_id
            },
            get_language_content("api_agent_success")
        )

    except Exception as e:
        # print(f"Error in agent_regenerate: {str(e)}")
        # print(traceback.format_exc())
        return response_error(get_language_content("api_agent_generate_failed"))


@router.post('/agent_supplement', response_model=ResAgentGenerateSchema)
async def agent_supplement(data: ReqAgentSupplementSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Supplement agent information based on existing agent and additional prompt

    Args:
        data (ReqAgentSupplementSchema): Request data containing:
            app_run_id (int): Original agent generation run ID
            supplement_prompt (str): Additional prompt for supplementing agent info
        userinfo (TokenData): User authentication information

    Returns:
        JSON response containing:
            app_run_id (int): The ID of the app run

    Raises:
        - Returns error if app_run_id is invalid
        - Returns error if record retrieval fails
    """
    # Validate app run exists and belongs to user
    app_run_info = AppRuns().select_one(
        columns=["id"],
        conditions=[
            {"column": "id", "value": data.app_run_id},
            {"column": "user_id", "value": userinfo.uid}
        ]
    )

    if not app_run_info:
        return response_error(get_language_content('app_run_error'))

    # Get first record to extract original user prompt
    first_record = AIToolLLMRecords().select_one(
        columns=['inputs', 'correct_prompt'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ],
        order_by="id ASC"
    )

    # Extract original user prompt from inputs
    base_user_prompt = ""
    inputs = first_record.get('inputs', {})
    if inputs is None:
        inputs = first_record.get('correct_prompt', {})

    try:
        if isinstance(inputs, dict) and 'user' in inputs:
            user_dict = inputs['user']
            if isinstance(user_dict, dict) and 'value' in user_dict:
                base_user_prompt = user_dict['value']
    except Exception:
        base_user_prompt = ""

    # Get latest record for agent history and status update
    last_record = AIToolLLMRecords().select_one(
        columns=['id', 'outputs'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ],
        order_by='id DESC'
    )

    # Extract agent info from outputs
    history_agent_info = {}
    try:
        if isinstance(last_record, dict) and 'outputs' in last_record:
            outputs_dict = last_record['outputs']
            if isinstance(outputs_dict, dict) and 'value' in outputs_dict:
                history_agent_info = outputs_dict['value']
    except Exception:
        pass

    system_prompt = get_language_content('agent_supplement_system', userinfo.uid)
    # system_prompt = system_prompt.format(
    #     append_prompt=get_language_content('agent_supplement_system', userinfo.uid, False)
    # )

    user_prompt = get_language_content('agent_supplement_user', userinfo.uid, False)
    user_prompt = user_prompt.format(
        agent_supplement=data.supplement_prompt,
        history_agent=history_agent_info
    )

    # Prepare input for LLM
    input_ = Prompt(system=system_prompt, user=base_user_prompt + user_prompt).to_dict()
    try:
        # Update app run status
        AppRuns().update(
            {'column': 'id', 'value': data.app_run_id},
            {'status': 1}
        )

        # Initialize new execution record
        record_id = AIToolLLMRecords().initialize_correction_record(
            app_run_id=data.app_run_id,
            ai_tool_type=1,
            correct_prompt=input_,
            user_prompt=data.supplement_prompt
        )

        if not record_id:
            return response_error(get_language_content("api_agent_generate_failed"))

        return response_success(
            {
                'app_run_id': data.app_run_id,
                'record_id': record_id
            },
            get_language_content("api_agent_success")
        )

    except Exception:
        return response_error(get_language_content("api_agent_generate_failed"))

@router.post('/agent_batch_generate', response_model=ResAgentBatchGenerateSchema)
async def agent_batch_generate(data: ReqAgentBatchGenerateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Batch generate agents

    Args:
        app_run_id: int, App run ID
        loop_count: int, Number of agents to generate per batch
        loop_limit: int, Total number of agents to generate
        supplement_prompt: str, Additional requirements for generation
        loop_id: int, Loop iteration ID
    """
    # 1: single generation, 2: multiple generation
    batch_generation_tool_mode = 1
    app_run_id = data.app_run_id
    if app_run_id <= 0:
        start_datetime_str = datetime.fromtimestamp(time()) \
            .replace(microsecond=0).isoformat(sep='_')
        app_run_id = AppRuns().insert({
            'user_id': userinfo.uid,
            'app_id': 0,
            'type': 2,
            'name': f'Agent_Generator_{start_datetime_str}',
            'status': 1  # Initial status
        })
    else:
        app_run_info = AppRuns().get_app_run_info(data.app_run_id, userinfo.uid)
        if not app_run_info:
            return response_error(get_language_content('app_run_error'))

    if data.loop_id > 0:
        # Continue existing batch
        loop_id = data.loop_id

        # Query whether there are unfinished records
        runing_record = AIToolLLMRecords().select_one(
            columns=['loop_id'],
            conditions=[
                {"column": "app_run_id", "value": data.app_run_id},
                {"column": "loop_id", "value": data.loop_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ],
            limit=1
        )
        if runing_record:
            # There are records that are being executed.
            return response_error(get_language_content("agent_batch_exist_runing_rocord"))
        
        record_loop_count = AIToolLLMRecords().get_record_loop_count(data.app_run_id, loop_id, batch_generation_tool_mode)
        remaining_count = data.loop_limit - record_loop_count
    else:
        # Start new batch
        loop_id = int(time())
        remaining_count = data.loop_limit

    loop_count = min(data.loop_count, remaining_count)

    if loop_count <= 0:
        return response_error(get_language_content("api_agent_batch_size_invalid"))
 
    try:
        record_list = AIToolLLMRecords().select(
            columns=['outputs'],
            conditions=[
                {"column": "app_run_id", "value": data.app_run_id},
                {"column": "loop_id", "value": loop_id}
            ],
            order_by='id ASC'
        )

        outputs_list = []
        for record in record_list:
            if record.get('outputs') and isinstance(record['outputs'], dict):
                output_value = record['outputs'].get('value')
                if isinstance(output_value, list):
                    outputs_list.extend(output_value)
                elif output_value:
                    outputs_list.append(output_value)

        model_info = Models().get_model_by_type(1, userinfo.team_id, uid=userinfo.uid)
        model_config_id = model_info['model_config_id']
        model_info = Models().get_model_by_config_id(model_config_id)
        outputs_list = truncate_messages_by_token_limit(outputs_list, model_info)

        if batch_generation_tool_mode is 2:
            system_prompt = get_language_content('agent_batch_generate_system', userinfo.uid)
            user_prompt = get_language_content('agent_batch_generate_user', userinfo.uid, False)
            user_prompt = user_prompt.format(
                agent_batch_requirements=data.supplement_prompt,
                agent_batch_number=loop_count,
                history_agents=outputs_list
            )
            input_ = Prompt(system=system_prompt, user=user_prompt).to_dict()
        else:
            # Prepare input with history outputs
            input_ = AIToolLLMRecords().inputs_append_history_outputs(
                app_run_id=data.app_run_id,
                loop_id=loop_id,
                agent_supplement=data.supplement_prompt,
                user_id=userinfo.uid
            )


        # Update app run status
        AppRuns().update(
            {'column': 'id', 'value': app_run_id},
            {'status': 1}
        )

        # Initialize execution record
        record_id = AIToolLLMRecords().initialize_execution_record(
            app_run_id=app_run_id,
            loop_limit=data.loop_limit,
            ai_tool_type=1,  # Agent generator type
            run_type=4,      # Batch generation
            loop_id=loop_id,
            loop_count=loop_count,
            inputs=input_,
            user_prompt=data.supplement_prompt,
            batch_generation_tool_mode=batch_generation_tool_mode,
            current_gen_count=loop_count
        )

        if not record_id:
            return response_error(get_language_content("api_agent_generate_failed"))

        return response_success(
            {
                "app_run_id": app_run_id,
                "loop_id": loop_id
            },
            get_language_content("api_agent_success")
        )

    except Exception as e:
        print(f"Error in agent_batch_generate: {str(e)}")
        print(traceback.format_exc())
        return response_error(get_language_content("api_agent_generate_failed"))


@router.post('/agent_save', response_model=ResAgentSaveSchema)
async def agent_save(data: ReqAgentSaveSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Save agent information

    Args:
        app_run_id: int, App run ID
        record_id: int, Record ID
        agent_info: dict, Agent information to save
    """
    app_run_info = AppRuns().select_one(
        columns=["id"],
        conditions=[
            {"column": "id", "value": data.app_run_id},
            {"column": "user_id", "value": userinfo.uid}
        ]
    )
    if not app_run_info:
        return response_error(get_language_content('app_run_error'))

    record_info = AIToolLLMRecords().select_one(
        columns=["id"],
        conditions=[
            {"column": "id", "value": data.record_id},
            {"column": "app_run_id", "value": data.app_run_id}
        ]
    )

    if not record_info:
        return response_error(get_language_content('api_agent_record_error'))

    agent_info = data.agent_info

    save_record = AIToolLLMRecords().update(
        {'column': 'id', 'value': record_info['id']},
        {'outputs': agent_info}
    )

    if not save_record:
        return response_error(get_language_content('api_agent_save_record_error'))

    return response_success(
        {
            "app_run_id": data.app_run_id,
            "record_id": record_info['id']
        },
        get_language_content("api_agent_success")
    )


@router.post("/agent_batch_sample", response_model=ResAgentBatchSample)
async def agent_batch_sample(data: ReqAgentBatchSample, userinfo: TokenData = Depends(get_current_user)):
    """
    Generate a sample agent based on user prompt

    Args:
        app_run_id: int, App run ID
        supplement_prompt: str, Additional requirements for sample generation
    """
    if not data.supplement_prompt:
        return response_error(get_language_content("api_agent_supplement_prompt_required"))
    
    
    app_run_id = data.app_run_id
    if app_run_id <= 0:
        start_datetime_str = datetime.fromtimestamp(time()) \
            .replace(microsecond=0).isoformat(sep='_')
        app_run_id = AppRuns().insert({
            'user_id': userinfo.uid,
            'app_id': 0,
            'type': 2,
            'name': f'Agent_Generator_{start_datetime_str}',
            'status': 1  # Initial status
        })
    else:
        AppRuns().update(
            {'column': 'id', 'value': app_run_id},
            {'status': 1}
        )
        app_run_info = AppRuns().select_one(
            columns=["id"],
            conditions=[
                {"column": "id", "value": app_run_id},
                {"column": "user_id", "value": userinfo.uid}
            ]
        )   
        if not app_run_info:
            return response_error(get_language_content('app_run_error'))

    # Prepare prompts for LLM
    system_prompt = get_language_content('agent_batch_sample_system', userinfo.uid)
    user_prompt = get_language_content('agent_batch_sample_user', userinfo.uid, False)
    
    user_prompt = user_prompt.format(
        agent_batch_requirements=data.supplement_prompt
    )

    input_ = Prompt(
        system=system_prompt,
        user=user_prompt
    ).to_dict()

    # Initialize LLM execution record
    record_id = AIToolLLMRecords().initialize_execution_record(
        app_run_id=app_run_id,
        ai_tool_type=5,  # Agent generator type
        inputs=input_,
        run_type=1,
        user_prompt=data.supplement_prompt
    )

    if not record_id:
        return response_error(get_language_content("api_agent_generate_failed"))

    # Return successful response
    return response_success(
        {
            "app_run_id": app_run_id,
            "record_id": record_id
        },
        get_language_content("api_agent_success")
    )


@router.post("/agent_create", response_model=ResBatchAgentCreateSchema)
async def agent_batch_create(data: ReqAgentBatchCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Create multiple agents in a single batch operation

    Args:
        data (ReqAgentBatchCreateSchema): List of agent configurations
        userinfo (TokenData): Current user authentication info

    Returns:
        ResBatchAgentCreateSchema: Contains list of created app IDs
    """
    agents_model = Agents()
    app_ids = []

    for agent_config in data.agents:
        result = agents_model.create_agent_with_configs(
            data=agent_config.dict(),
            user_id=userinfo.uid,
            team_id=userinfo.team_id
        )

        if result["status"] == 1:
            app_ids.append(result["app_id"])
        else:
            # Continue with remaining agents even if one fails
            continue

    if not app_ids:
        return response_error(get_language_content("api_agent_batch_create_failed"))

    return response_success(
        data={"app_ids": app_ids},
        detail=get_language_content("api_agent_success")
    )


@router.get("/{agent_id}/agent_message_list", response_model=AgentResponseBase, summary="Retrieve the list of historical messages from the intelligent agent")
async def agent_message_list(agent_id: int, page: int = 1, page_size: int = 10, userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve the message list for a specific Agent chat.
    This endpoint retrieves chat information about agents and provides services for users who need to view chat history and participants.
    Parameters:
    -Agent_id (int): A unique identifier used to retrieve the chat message of the agent. Compulsory.
    -Userinfo (TokenData): Information about the current user is provided through dependency injection. Compulsory.

    Returns:
    -A response object containing Agent chat messages and a list of joined agents, formatted according to the AgentResponse Base model.

    Raises:
    -HTTPException: If 'agent_id' is invalid, it indicates that the user has not been authenticated or the agent does not exist.
    """
    find_agent = Agents().get_agent_by_id_info(agent_id, userinfo.uid)
    if not find_agent:
        return response_error(get_language_content("agent_does_not_exist"))

    agent_msg_list = AgentChatMessages().history_agent_messages(
        agent_id=agent_id,
        uid=userinfo.uid,
        page=page,
        page_size=page_size
    )

    return response_success(agent_msg_list)


@router.get("/{agent_id}/agent_log_list", response_model=AgentLogListResponse, summary="Agent log list")
async def agent_log_list(agent_id: int, page: int = 1, page_size: int = 10, userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch a list of all chat rooms.
    This endpoint fetches a paginated list of all available chat rooms, allowing users to optionally filter the results by a name. The pagination is controlled through the page number and page size parameters.

    Parameters:
    - page (int): The current page number for pagination. Defaults to 1.
    - page_size (int): The number of chat rooms to return per page. Defaults to 10.
    -Agent_id (int): A unique identifier used to retrieve the chat message of the agent. Compulsory.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    The successful response containing the Agent operation log is formatted according to the AgentLogListResponse model.

    Raises:
    - HTTPException: If there are issues with pagination parameters or if the user is not authenticated.
    """
    find_agent = Agents().get_agent_by_id_info(agent_id, userinfo.uid)
    if not find_agent:
        return response_error(get_language_content("agent_does_not_exist"))

    result = AppRuns().all_agent_log_list(
        page=page,
        page_size=page_size,
        user_id=userinfo.uid,
        agent_id=agent_id)
    return response_success(result)


@router.get("/{agent_id}/agent_log_details", response_model=AgentLogDetailResponse, summary="Agent log Details")
async def agent_log_list(agent_id: int, app_run_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch a list of all chat rooms.
    This endpoint fetches a paginated list of all available chat rooms, allowing users to optionally filter the results by a name. The pagination is controlled through the page number and page size parameters.

    Parameters:
    - Agent_id (int): A unique identifier used to retrieve the chat message of the agent. Compulsory.
    - app_run_id (int): A unique identifier used to retrieve the chat message of the agent. Compulsory.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    The successful response containing the Agent operation log is formatted according to the AgentLogDetailResponse model.

    Raises:
    - HTTPException: If there are issues with pagination parameters or if the user is not authenticated.
    """
    find_agent = Agents().get_agent_by_id_info(agent_id, userinfo.uid)
    if not find_agent:
        return response_error(get_language_content("agent_does_not_exist"))

    result = AppRuns().select_one(
        columns=['id', 'user_id', 'app_id', 'agent_id', 'workflow_id', 'dataset_id', 'tool_id', 'chatroom_id', 'type',
                 'name', 'graph', 'inputs', 'raw_user_prompt', 'model_data', 'knowledge_base_mapping', 'level',
                 'context', 'completed_edges', 'skipped_edges', 'status', 'completed_steps', 'actual_completed_steps',
                 'need_human_confirm', 'need_correct_llm', 'error', 'outputs', 'elapsed_time', 'prompt_tokens',
                 'completion_tokens', 'total_tokens', 'embedding_tokens', 'reranking_tokens', 'total_steps',
                 'created_time', 'updated_time', 'finished_time'],
        conditions=[
            {"column": "agent_id", "value": agent_id},
            {"column": "user_id", "value": userinfo.uid},
            {"column": "id", "value": app_run_id},
            {'column': 'status', 'op': 'in', 'value': [3, 4]}
        ]
    )

    if not result:
        return response_error(get_language_content("app_run_error"))
    return response_success(result)


@router.post("/{agent_id}/clear_agent_chat_memory", response_model=ClearAgentChatMemory, summary="Clear agent chat memory")
async def clear_agent_chat_memory(agent_id: int, message_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Clear the chat memory for a specific Agent chat.
    This endpoint allows users to clear the chat history of a specific agent chat room,
    removing all messages associated with the provided message ID.

    Parameters:
    - agent_id (int): A unique identifier used to specify the agent whose chat memory needs to be cleared. Compulsory.
    - message_id (int): A unique identifier used to specify the message or chat session to be cleared. Compulsory.
    - userinfo (TokenData): Information about the current user is provided through dependency injection. Compulsory.

    Returns:
    - A response object formatted according to the AgentResponseBase model, indicating the success or failure of the operation.

    Raises:
    - HTTPException:
        - If 'agent_id' is invalid, it indicates that the user has not been authenticated or the agent does not exist.
        - If 'message_id' is invalid, it indicates that the specified message or chat session does not exist.
    """

    find_agent = Agents().get_agent_by_id_info(agent_id, userinfo.uid)
    if not find_agent:
        return response_error(get_language_content("agent_does_not_exist"))
    find_message = AgentChatMessages().select_one(
        columns=['id'],
        conditions=[
            {"column": "agent_id", "value": agent_id},
            {"column": "user_id", "value": userinfo.uid},
            {"column": "id", "value": message_id}
        ]
    )['id']
    if not find_message:
        return response_error(get_language_content("agent_message_does_not_exist"))

    AgentChatMessages().update(
        {'column': 'id', 'value': find_message},
        {'history_cleared': 1}
    )

    return response_success(
        {"message_id": find_message}
    )


@router.post("/agent_chat_message", response_model=ResAgentRunSchemaReturn)
async def agent_chat_message(data: AgentChatMessage, userinfo: TokenData = Depends(get_current_user)):
    """
    agent run

    agent_id: int, Agent id
    ability_id: int, Ability id
    input_dict: dict, Input data
    prompt: dict, Prompt data
    """
    agent_id = data.agent_id
    ability_id = data.ability_id
    input_dict = data.input_dict
    prompt = data.prompt
    uid = userinfo.uid
    team_id = userinfo.team_id
    message = data.message

    if agent_id <= 0:
        return response_error(get_language_content("api_agent_run_agent_id_required"))
    if not input_dict:
        return response_error(get_language_content("api_agent_run_input_dict_required"))
    try:
        create_variable_from_dict(input_dict)
    except:
        return response_error(get_language_content("api_agent_run_input_dict_wrong"))
    if not prompt:
        return response_error(get_language_content("api_agent_run_prompt_required"))
    try:
        create_prompt_from_dict(prompt)
    except:
        return response_error(get_language_content("api_agent_run_prompt_wrong"))

    # get agent
    agents_model = Agents()
    agent = agents_model.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": agent_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]
    )
    if not agent:
        return response_error(get_language_content("api_agent_run_agent_error"))
    if agent["user_id"] != uid:
        if agent["status"] != 1:
            return response_error(get_language_content("api_agent_run_agent_status_not_normal"))
        if agent["publish_status"] != 1:
            return response_error(get_language_content("api_agent_run_not_creators"))

    # get app
    apps_model = Apps()
    app = apps_model.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": agent["app_id"]},
            {"column": "team_id", "value": team_id},
            {"column": "mode", "value": 1},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]
    )
    if not app:
        return response_error(get_language_content("api_agent_run_app_error"))
    if app["user_id"] != uid:
        if app["is_public"] == 0:
            return response_error(get_language_content("api_agent_run_team_not_open"))
        if app["status"] != 1:
            return response_error(get_language_content("api_agent_run_app_status_not_normal"))

    # get agent ability
    if ability_id != 0:
        agent_abilities_model = AgentAbilities()
        ability = agent_abilities_model.select_one(
            columns="*",
            conditions=[
                {"column": "id", "value": ability_id},
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not ability:
            return response_error(get_language_content("api_agent_run_ability_error"))
        if ability["user_id"] != uid and ability["status"] != 1:
            return response_error(get_language_content("api_agent_run_ability_status_not_normal"))

    # Insert Message
    message_id = AgentChatMessages().insert({
        'user_id': userinfo.uid,
        'agent_id': agent_id,
        'message': message
    })

    run_app.delay(app_type="agent", id_=agent_id, user_id=uid, input_dict=input_dict, ability_id=ability_id, prompt=prompt, is_chat=True)
    return response_success({"message_id": message_id, "detail": get_language_content("api_agent_success")})


@router.get("/{agent_id}/chatrooms", summary="Get chat rooms for an agent", response_model=ResAgentChatRoomsSchema)
async def get_agent_chatrooms(agent_id: int, page: int = 1, page_size: int = 10, all: bool = False,
                              userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve the list of chat rooms in which the specified agent is present.
    Supports pagination; if 'all' is True, returns all records.
    """
    result = Chatrooms().get_chatrooms_by_agent(agent_id, page, page_size, show_all=all)
    return response_success(result)

