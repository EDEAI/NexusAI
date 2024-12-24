from fastapi import APIRouter
from core.database.models import CustomTools, Apps
from api.schema.skill import *
from api.utils.common import *
from api.utils.jwt import *
from core.workflow.variables import *
from core.workflow.nodes import *
from celery_app import run_app
from languages import get_language_content


router = APIRouter()
tools_db = CustomTools()
apps_db = Apps()
nodes = Nodes()


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
        return response_error(get_language_content("publish_status can only input 0 or 1"))

    if tool_data['publish_status'] == 1:
        tool_data['published_time'] = datetime.now()
    tool_id = tools_db.insert(tool_data)
    return response_success({'id': tool_id})


# Read all custom tool
@router.get("/skill_list", response_model=ResSkillListSchema)
async def skill_list(page: int = 1, page_size: int = 10, skill_search_type: int = 1,  name: str = "",userinfo: TokenData = Depends(get_current_user)):
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
async def skill_info( app_id: int, publish_status: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Read all custom tool
    :param app_id: The app_id of the skill.
    :param publish_status: int, skill publish status 0: Draft 1: Published.
    :param userinfo: The userinfo of the skill.
    :return: ID of created skills
    """
    if app_id <= 0:
        return response_error(get_language_content("Invalid app_id"))
    if publish_status not in [0, 1]:
        return response_error(get_language_content("publish_status can only input 0 or 1"))
    result = tools_db.get_skill_info(userinfo.uid, app_id, publish_status,userinfo.team_id)
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
        return response_error(get_language_content("is_public can only input 0 or 1"))
    try:
        if 'is_public' in update_data:
            apps_data = {
                "is_public": update_data['is_public'],
                "updated_time": update_data['updated_time']
            }
            apps_db.update([{'column': 'id', 'value': app_id}], apps_data)
            del update_data['is_public']
        conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id},
                      {'column': 'publish_status', 'value': 0}]
        tools_db.update(conditions, update_data)
        return response_success()
    except:
        return response_error(get_language_content("update error"))

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
    app = Datasets().get_app_by_id(app_id)
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
        tools_db.update([{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id}, {'column': 'publish_status', 'value': 1}], tool_data)
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
        return response_error(get_language_content("app_id is required"))

    conditions = [{'column': 'app_id', 'value': app_id}, {'column': 'user_id', 'value': user_id}]
    app_conditions = [{'column': 'id', 'value': app_id}]
    deleted = tools_db.soft_delete(conditions)
    apps_db.soft_delete(app_conditions)
    if not deleted:
        return response_error(get_language_content("Tool not found"))
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
        return response_error(get_language_content("Tool not found"))
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
        return response_error(get_language_content("Tool not found"))
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
        return response_error(get_language_content("skill_id is required"))

    if not input_dict:
        return response_error(get_language_content("input_dict is required"))

    try:
        create_variable_from_dict(input_dict)
    except:
        return response_error(get_language_content("input_dict data in wrong format"))

    skill = tools_db.select_one(
        columns="*",
        conditions=[
            {"column": "id", "value": skill_id},
            {"column": "team_id", "value": team_id},
            {"column": "status", "op": "in", "value": [1, 2]}
        ])
    if not skill:
        return response_error(get_language_content("skill error"))

    if skill["user_id"] != uid:
        if skill["status"] != 1:
            return response_error(get_language_content("The agent  skill is not normal"))
        if skill["publish_status"] != 1:
            return response_error(get_language_content("Only creators can run drafts skill"))

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
        return response_error(get_language_content("app error"))
    if app["user_id"] != uid:
        if app["is_public"] == 0:
            return response_error(get_language_content("Team members are not open"))
        if app["status"] != 1:
            return response_error(get_language_content("The app status is not normal"))
    task = run_app.delay(app_type="skill", id_=skill_id, user_id=uid, input_dict=input_dict)
    result = task.get()
    if result["status"] != "success":
        return response_error(get_language_content(result["message"]))
    return response_success({"outputs": result["data"]["outputs"]})


