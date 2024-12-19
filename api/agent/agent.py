from fastapi import APIRouter, Request
from api.utils.common import *
from api.utils.jwt import *
from api.schema.agent import *
from api.schema.base import *
from core.database.models.agents import Agents
from core.database.models.apps import Apps
from core.database.models.agent_abilities import AgentAbilities
from core.workflow.nodes import AgentNode
from core.workflow.variables import create_variable_from_dict
from core.llm.prompt import create_prompt_from_dict, Prompt
from celery_app import run_app
from languages import get_language_content

router = APIRouter()

@router.get("/agent_list", response_model = ResAgentListSchema)
async def agent_list(page: int = 1, page_size: int = 10, agent_search_type: int = 1, name: str = "", userinfo: TokenData = Depends(get_current_user)):
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

@router.put("/agent_base_update/{agent_id}", response_model = ResAgentBaseCreateSchema)
async def agent_base_update(request: Request, agent_id: int, data: ReqAgentBaseCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    agent base update

    agent_id: int, Agent id
    is_public: int, Is it open to team members? 0: No 1: Yes
    enable_api: int, Whether to enable API 0: No 1: Yes
    obligations: str, Agent obligations
    input_variables: dict, Input variables
    dataset_ids: list, Multiple dataset id
    m_config_id: int, Model configuration ID
    allow_upload_file: int, Is it allowed to upload files? 0: No 1: Yes
    default_output_format: int, Default output format 1: text 2: json 3: code
    """
    is_public = data.is_public
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
    result = agents_model.agent_base_update(agent_id, userinfo.uid, userinfo.team_id, is_public, enable_api, obligations, input_variables, dataset_ids, m_config_id, allow_upload_file, default_output_format)
    if result["status"] != 1:
        return response_error(result["message"])
    app_id = result["data"]["app_id"]

    return response_success(result["data"], get_language_content("api_agent_success"))

@router.put("/agent_abilities_set/{agent_id}", response_model = RespBaseSchema)
async def agent_abilities_set(agent_id: int, data: ReqAgentAbilitiesSetSchema, userinfo: TokenData = Depends(get_current_user)):
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

@router.put("/agent_publish/{agent_id}", response_model = RespBaseSchema)
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

@router.delete("/agent_delete/{app_id}", response_model = RespBaseSchema)
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

@router.get("/agent_info/{app_id}", response_model = ResAgentInfoSchema)
async def agent_info(app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
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

@router.post("/agent_run", response_model = ResAgentRunSchema)
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
        columns = "*",
        conditions = [
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
        columns = "*",
        conditions = [
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
            columns = "*",
            conditions = [
                {"column": "id", "value": ability_id},
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not ability:
            return response_error(get_language_content("api_agent_run_ability_error"))
        if ability["user_id"] != uid and ability["status"] != 1:
            return response_error(get_language_content("api_agent_run_ability_status_not_normal"))

    task = run_app.delay(app_type = "agent", id_ = agent_id, user_id=uid, input_dict = input_dict, ability_id = ability_id, prompt = prompt)
    result = task.get()
    if result["status"] != "success":
        return response_error(result["message"])

    return response_success({"outputs": result["data"]["outputs"], "outputs_md": result["data"]["outputs_md"]}, get_language_content("api_agent_success"))