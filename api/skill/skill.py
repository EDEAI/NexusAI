import asyncio
from fastapi import APIRouter
from core.database.models.tag_bindings import TagBindings
from core.database.models import CustomTools, Apps
from api.schema.skill import *
from api.utils.common import *
from api.utils.jwt import *
from core.workflow.variables import *
from core.workflow.nodes import *
from celery_app import run_app
from languages import get_language_content
from core.database.models.app_runs import AppRuns
from core.database.models.ai_tool_llm_records import AIToolLLMRecords
from core.llm.prompt import create_prompt_from_dict, Prompt

from core.helper import extract_file_list_from_skill_output
from time import time
import os

router = APIRouter()
tools_db = CustomTools()
apps_db = Apps()
nodes = Nodes()
tagbindings = TagBindings()


# Create custom tool
@router.post("/skill_create", response_model=ResSkillCreateSchema)
async def skill_create(tool: ReqSkillCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
        Create custom tool
        :param tool: The tool to create.
        :param userinfo: The userinfo of the skill.
        :return: ID of created skills
    """
    tool_data = tool.dict(exclude_unset=True)
    tool_data['user_id'] = userinfo.uid
    tool_data['team_id'] = userinfo.team_id
    tool_data['created_time'] = datetime.now()
    tool_data['updated_time'] = datetime.now()
    tool_data['status'] = 1
    if 'publish_status' not in tool_data or tool_data['publish_status'] not in [0, 1]:
        return response_error(get_language_content("publish_status_invalid"))

    if tool_data['publish_status'] == 1:
        tool_data['published_time'] = datetime.now()
    tool_id = tools_db.insert(tool_data)
    return response_success({'id': tool_id})


# Read all custom tool
@router.get("/skill_list", response_model=ResSkillListSchema)
async def skill_list(page: int = 1, page_size: int = 10, skill_search_type: int = 1, name: str = "",
                     userinfo: TokenData = Depends(get_current_user)):
    """
        Read all custom tool
        :param page: The page of the skill.
        :param page_size: The page_size of the skill.
        :param skill_search_type: The skill_search_type of the skill 1: my skill 2: team skill 3: select my skill.
        :param name: The name of the skill.0.
        :param userinfo: The userinfo of the skill.
        :return: ID of created skills
    """
    user_id = userinfo.uid
    team_id = userinfo.team_id
    result = tools_db.skill_list(page, page_size, user_id, team_id, skill_search_type, name)
    return response_success(result)


# Read single custom tool
@router.get("/skill_info/{app_id}", response_model=ResSkillBaseInfoSchema)
async def skill_info(app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Read all custom tool
    :param app_id: The app_id of the skill.
    :param publish_status: int, skill publish status 0: Draft 1: Published.
    :param userinfo: The userinfo of the skill.
    :return: ID of created skills
    """
    if app_id <= 0:
        return response_error(get_language_content("invalid_app_id"))
    if publish_status not in [0, 1]:
        return response_error(get_language_content("publish_status_invalid"))
    result = tools_db.get_skill_info(userinfo.uid, app_id, publish_status, userinfo.team_id)
    if result["status"] != 1:
        return response_error(get_language_content(result["message"]))

    return response_success(result["data"])


# Update custom tool
@router.put("/skill_update/{app_id}")
async def skill_update(app_id: int, tool: ReqSkillUpdateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Update custom tool
    :param app_id: The app_id of the skill.
    :param tool: The tool to update.
    :param userinfo: The userinfo of the skill.
    :param is_public: int, Is it open to team members? 0: No 1: Yes.
    :return: ID of created skills
    """
    user_id = userinfo.uid
    update_data = tool.dict(exclude_unset=True)
    update_data['updated_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if 'is_public' in update_data and update_data['is_public'] not in [0, 1]:
        return response_error(get_language_content("is_public_invalid"))

    if 'attrs_are_visible' in update_data and update_data['attrs_are_visible'] not in [0, 1]:
        return response_error(get_language_content("api_agent_base_update_attrs_are_visible_error"))
    try:
        if 'is_public' in update_data:
            apps_data = {
                "is_public": update_data['is_public'],
                "updated_time": update_data['updated_time']
            }
            apps_db.update([{'column': 'id', 'value': app_id}], apps_data)
            del update_data['is_public']

        if 'attrs_are_visible' in update_data:
            apps_data = {
                "attrs_are_visible": update_data['attrs_are_visible'],
                "updated_time": update_data['updated_time']
            }
            apps_db.update([{'column': 'id', 'value': app_id}], apps_data)
            del update_data['attrs_are_visible']
        conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id},
                      {'column': 'publish_status', 'value': 0}]
        tools_db.update(conditions, update_data)

        return response_success()
    except:
        return response_error(get_language_content("update_error"))


@router.put("/skill_publish/{app_id}", response_model=ResSkillPublishSchema)
async def skill_publish(app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
        publish skill
        :param app_id: The app_id of the skill to publish.
        :param userinfo: The userinfo of the skill.
        :return: ID of published skills
    """

    user_id = userinfo.uid
    draft_info = tools_db.get_publish_skill_info(user_id, app_id, 0)
    if draft_info['status'] == 2:
        return response_error(get_language_content("Skill do not exist"))
    draft_info = draft_info['data']
    app = Apps().get_app_by_id(app_id)
    node = SkillNode(
        title=app['name'],
        desc=app['description'],
        input=create_variable_from_dict(draft_info['input_variables']),
        skill_id=draft_info['id']
    )
    try:
        node.validate()
    except Exception as e:
        return response_error(str(e))

    tool_data = {
        "team_id": draft_info['team_id'],
        "user_id": draft_info['user_id'],
        "app_id": draft_info['app_id'],
        "config": draft_info['config'],
        "input_variables": draft_info['input_variables'],
        "dependencies": draft_info['dependencies'],
        "code": draft_info['code'],
        "output_type": draft_info['output_type'],
        "output_variables": draft_info['output_variables'],
        "publish_status": 1,
        "published_time": datetime.now(),
        "status": 1
    }
    publish_info = tools_db.get_publish_skill_info(user_id, app_id, 1)

    if publish_info['status'] == 2:
        tool_id = tools_db.insert(tool_data)
        return response_success({'id': tool_id})
    else:
        tools_db.update([{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id},
                         {'column': 'publish_status', 'value': 1}], tool_data)
        apps_data = {
            "publish_status": 1,
            "updated_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        apps_db.update([{'column': 'id', 'value': app_id}], apps_data)
        return response_success({'id': 0})


@router.delete("/delete_skill_by_app_id/{app_id}")
async def delete_skill_by_app_id(app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
        Remove skills through appid
        :param app_id: The app_id of the skill.
        :param userinfo: The userinfo of the skill.
        :return: ID of deleted skills
    """
    user_id = userinfo.uid
    if app_id <= 0:
        return response_error(get_language_content("app_id_required"))

    conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id}]
    app_conditions = [{'column': 'id', 'value': app_id}]
    deleted = tools_db.soft_delete(conditions)
    apps_db.soft_delete(app_conditions)
    if not deleted:
        return response_error(get_language_content("skill_not_found"))
    return response_success()


# Soft delete custom tool
@router.put("/skill_delete/{id}/soft")
async def skill_soft_delete(id: int, userinfo: TokenData = Depends(get_current_user)):
    """
        Soft delete custom tool
        :param id: The id of the skill.
        :param userinfo: The userinfo of the skill.
        :return: ID of deleted skills
    """
    user_id = userinfo.uid
    conditions = [{'column': 'id', 'value': id}, {'column': 'user_id', 'value': user_id}]
    deleted = tools_db.soft_delete(conditions)
    if not deleted:
        return response_error(get_language_content("skill_not_found"))
    return response_success()


# Hard delete custom tool
@router.delete("/skill_delete/{app_id}")
async def skill_delete(app_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete custom tool
    :param app_id: The app_id of the skill.
    :param userinfo: The userinfo of the skill.
    """
    user_id = userinfo.uid
    conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id}]
    deleted = tools_db.delete(conditions)
    if not deleted:
        return response_error(get_language_content("skill_not_found"))
    return response_success()


@router.post("/skill_run", response_model=ResSkillRunSchema)
async def skill_run(data: ReqSkillRunSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Run skill
    input_dict: dict, Input data
    prompt: dict, Prompt data
    """
    skill_id = data.skill_id
    input_dict = data.input_dict
    uid = userinfo.uid
    team_id = userinfo.team_id

    if skill_id <= 0:
        return response_error(get_language_content("skill_id_required"))

    if not input_dict:
        return response_error(get_language_content("input_dict_required"))

    try:
        create_variable_from_dict(input_dict)
    except:
        return response_error(get_language_content("input_dict_format_error"))

    skill = tools_db.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "op": "in", "value": [1, 2]}
        ])
    if not skill:
        return response_error(get_language_content("skill_error"))

    if skill["user_id"] != uid:
        if skill["status"] != 1:
            return response_error(get_language_content("skill_status_not_normal"))
        if skill["publish_status"] != 1:
            return response_error(get_language_content("skill_draft_creators_only"))

    apps_model = Apps()
    app = apps_model.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill["app_id"]},
            {"column": "team_id", "value": team_id},
            {"column": "mode", "value": 4},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]
    )

    if not app:
        return response_error(get_language_content("app_error"))
    if app["user_id"] != uid:
        if app["is_public"] == 0:
            return response_error(get_language_content("team_members_not_open"))
        if app["status"] != 1:
            return response_error(get_language_content("app_status_not_normal"))
    task = run_app.delay(app_type="skill", id_=skill_id, user_id=uid, input_dict=input_dict)
    while not task.ready():
        await asyncio.sleep(0.1)
    result = task.get()
    if result["status"] != "success":
        return response_success({"outputs":{
                'error': result["message"]
            }})

    outputs = result["data"]["outputs"]
    file_list = []

    if skill and skill.get("output_variables"):
        file_list = extract_file_list_from_skill_output(outputs, skill["output_variables"])
    return response_success({
        "outputs": outputs,
        "file_list": file_list
    })


@router.post("/skill_generate", response_model=ResSkillGenerateSchema)
async def skill_generate(data: ReqSkillGenerateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Generate skill based on user prompt using LLM

    Args:
        data: Request data containing user prompt for skill generation
        userinfo: User authentication info

    Returns:
        Dictionary containing:
        - app_run_id: ID of the app run record
        - record_id: ID of the LLM execution record

    Flow:
        1. Validates user prompt
        2. Creates app run record
        3. Prepares system and user prompts for LLM
        4. Initializes LLM execution record
        5. Returns record IDs for tracking generation progress
    """
    # Validate user prompt
    if not data.user_prompt:
        return response_error(get_language_content("api_skill_user_prompt_required"))

    # Create app run record
    start_datetime_str = datetime.fromtimestamp(time()) \
        .replace(microsecond=0).isoformat(sep='_')
    app_run_id = AppRuns().insert({
        'user_id': userinfo.uid,
        'app_id': 0,
        'type': 2,  # Skill generator type
        'name': f'Skill_Generator_{start_datetime_str}',
        'status': 1  # Initial status
    })

    # Prepare prompts for LLM
    system_prompt = get_language_content('generate_skill_system_prompt', userinfo.uid)
    user_prompt = get_language_content('generate_skill_user', userinfo.uid, False)

    user_prompt = user_prompt.format(
        user_prompt=data.user_prompt
    )

    input_ = Prompt(
        system=system_prompt,
        user=user_prompt
    ).to_dict()

    # Initialize LLM execution record
    record_id = AIToolLLMRecords().initialize_execution_record(
        app_run_id=app_run_id,
        ai_tool_type=2,  # Skill generator type
        inputs=input_,
        run_type=1,
        user_prompt=data.user_prompt
    )

    if not record_id:
        return response_error(get_language_content("api_skill_generate_failed"))

    # Return successful response
    return response_success(
        {
            "app_run_id": app_run_id,
            "record_id": record_id
        },
        get_language_content("api_skill_success")
    )


@router.post("/skill_correction", response_model=ResSkillCorrectionSchema)
async def skill_correction(data: ReqSkillCorrectionSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Correct/improve existing skill based on user feedback using LLM

    Args:
        data: Request data containing:
            - app_run_id: ID of original skill generation run
            - correction_prompt: User feedback for improvement
        userinfo: User authentication info

    Returns:
        Dictionary containing:
        - app_run_id: ID of the app run record
        - record_id: ID of the new LLM correction record

    Flow:
        1. Validates app run exists and belongs to user
        2. Retrieves original generation context and results
        3. Prepares correction prompts with original context
        4. Creates new LLM execution record for correction
        5. Returns record IDs for tracking correction progress
    """
    # Validate app run id
    app_run_info = AppRuns().select_one(
        columns=["id"],
        conditions=[
            {"column": "id", "value": data.app_run_id},
            {"column": "user_id", "value": userinfo.uid}
        ]
    )

    if not app_run_info:
        return response_error(get_language_content('app_run_error'))

    first_record = AIToolLLMRecords().select_one(
        columns=['id', 'inputs', 'correct_prompt'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ],
        order_by='id ASC'
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

    # Get first record to extract original user prompt
    last_record = AIToolLLMRecords().select_one(
        columns=['id', 'outputs', 'correct_prompt'],
        conditions=[
            {"column": "app_run_id", "value": data.app_run_id}
        ],
        order_by='id DESC'
    )

    # Extract agent info from outputs
    history_skill_info = {}
    try:
        if isinstance(last_record, dict) and 'outputs' in last_record:
            outputs_dict = last_record['outputs']
            if isinstance(outputs_dict, dict) and 'value' in outputs_dict:
                history_skill_info = outputs_dict['value']
    except Exception:
        pass

    system_prompt = get_language_content('correction_skill_system_prompt', userinfo.uid)

    user_prompt = get_language_content('correction_skill_user', userinfo.uid, False)
    user_prompt = user_prompt.format(
        correction_prompt=data.correction_prompt,
        history_skill=history_skill_info
    )

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
            ai_tool_type=2,
            correct_prompt=input_,
            user_prompt=data.correction_prompt
        )

        if not record_id:
            return response_error(get_language_content("api_skill_generate_failed"))

        return response_success(
            {
                'app_run_id': data.app_run_id,
                'record_id': record_id
            },
            get_language_content("api_skill_success")
        )
    except Exception:
        return response_error(get_language_content("api_skill_correction_failed"))


@router.post("/skill_data_create", response_model=ResSkillCreateSchema)
async def skill_data_create(data: ReqSkillDataCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Create or update skill data with structured format
    Args:
        data: The skill data with standardized format including optional app_id
        userinfo: The userinfo of the skill
    Returns:
        ID of created/updated skills
    """
    # No need to convert to dict here since we want to use Pydantic model properties
    result = tools_db.skill_data_create(
        data.dict(exclude_unset=True),
        userinfo.uid,
        userinfo.team_id
    )

    if result["status"] != 1:
        return response_error(result["message"])

    return response_success({
        'id': result["skill_id"],
        'app_id': result["app_id"]
    })


@router.post("/skill_debug", response_model=ResSkillRunSchema)
async def skill_debug(data: ReqSkillDebugSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Debug skill by running it with test data without saving
    Args:
        data: The skill configuration and test data
        userinfo: The user info object
    Returns:
        Execution results of the skill
    """
    task = run_app.delay(app_type="skill", id_=0, user_id=userinfo.uid, input_dict=data.test_input,
                         custom_data=data.dict(exclude_unset=True))
    while not task.ready():
        await asyncio.sleep(0.1)
    try:
        result = task.get()
        if result["status"] != "success":
            return response_success({"outputs":{
                'error': result["message"]
            }})
        return response_success({"outputs": result["data"]["outputs"]})
    except Exception as e:
        return response_error(str(e))
