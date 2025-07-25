import os
from fastapi import APIRouter
from core.database.models import Apps
from core.database.models.agents import Agents
from core.database.models.custom_tools import CustomTools
from core.database.models.datasets import Datasets
from core.database.models.workflows import Workflows
from core.database.models import (
    Models,
    ModelConfigurations,
    Teams,
    Roles
)
from config import *
from log import Logger
from core.dataset import DatasetManagement
logger = Logger.get_logger('vector')
from api.utils.common import *
from api.schema.apps import *
from api.utils.jwt import *

from languages import get_language_content
from api.utils.auth import get_uid_user_info

os.environ['DATABASE_AUTO_COMMIT'] = 'False'
router = APIRouter()

@router.get('/apps_list', response_model=ResAppListSchema, summary="Fetching a Paginated List of Applications for the Current User or Team")
async def get_app_list(page: int, page_size: int, search_type: int, apps_name: str = "", apps_mode: str = "", tag_ids: str = "", userinfo: TokenData = Depends(get_current_user)):
    """
    Fetch a paginated list of applications for the current user or team.

    This endpoint fetches a detailed and searchable list of all published applications associated with the current user or their team. It includes various types of applications such as agents, workflows, skills, databases, and chatrooms, offering a comprehensive overview of the available applications.

    Parameters:
    - page (int): The page number for pagination. Determines which page of results to display. Required.
    - page_size (int): The number of apps to list per page. Required.
    - search_type (int): The category of apps to search for. It must be either 1 or 2, with each number corresponding to a specific filter or category. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object containing the paginated list of apps, structured according to the ResAppListSchema model.

    Raises:
    - HTTPException: If the 'search_type' is not valid, or if the user is not properly authenticated.
    """

    if search_type not in [1, 2, 3]:
        return response_error(get_language_content("app_search_type"))

    request = Apps().get_app_list(page, page_size, search_type, apps_name, apps_mode, userinfo.uid, userinfo.team_id, tag_ids)
    if search_type in [1, 3]:
        agent_model = Agents()
        agent_info = agent_model.select(
            columns=[
                'app_id', 'published_time', 'id as agent_id'
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "user_id", "value": userinfo.uid},
            ]
        )

        agent_publish_time = {}
        agent_ids = {}

        for agent_item in agent_info:
            agent_publish_time[agent_item['app_id']] = agent_item['published_time']
            agent_ids[agent_item['app_id']] = agent_item['agent_id']

        workflow_model = Workflows()
        workflow_info = workflow_model.select(
            columns=[
                'app_id', 'published_time'
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "user_id", "value": userinfo.uid},
            ]
        )
        workflow_publish_time = {}

        for workflow_item in workflow_info:
            workflow_publish_time[workflow_item['app_id']] = workflow_item['published_time']

        skill_model = CustomTools()
        skill_info = skill_model.select(
            columns=[
                'id as skill_id', 'app_id', 'published_time'
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "user_id", "value": userinfo.uid},
            ]
        )
        skill_publish_time = {}
        skill_ids = {}
        for skill_item in skill_info:
            skill_publish_time[skill_item['app_id']] = skill_item['published_time']
            skill_ids[skill_item['app_id']] = skill_item['skill_id']

        for item in request['list']:
            if item['mode'] == 1:
                item['agent_id'] = agent_ids.get(item['app_id'])
                if item['publish_status'] == 1:
                    item['published_time'] = agent_publish_time[item['app_id']]
                else:
                    item['published_time'] = None
            elif item['mode'] == 2:
                if item['publish_status'] == 1:
                    item['published_time'] = workflow_publish_time[item['app_id']]
                else:
                    item['published_time'] = None
            elif item['mode'] == 3:
                item['published_time'] = None
            elif item['mode'] == 4:
                item['skill_id'] = skill_ids.get(item['app_id'])
                if item['publish_status'] == 1:
                    item['published_time'] = skill_publish_time[item['app_id']]
                else:
                    item['published_time'] = None

    if search_type == 2:
        agent_model = Agents()
        agent_info = agent_model.select(
            columns=[
                'app_id', 'published_time', 'users.nickname', 'id as agent_id'
            ],
            joins=[
                ["left", "users", "users.id = agents.user_id"],
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "team_id", "value": userinfo.team_id},
            ]
        )

        agent_publish_time = {}
        agent_publish_creator = {}
        agent_ids = {}
        for agent_item in agent_info:
            agent_publish_time[agent_item['app_id']] = agent_item['published_time']
            agent_publish_creator[agent_item['app_id']] = agent_item['nickname']
            agent_ids[agent_item['app_id']] = agent_item['agent_id']

        workflow_model = Workflows()
        workflow_info = workflow_model.select(
            columns=[
                'app_id', 'published_time', 'users.nickname'
            ],
            joins=[
                ["left", "users", "users.id = workflows.user_id"],
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "team_id", "value": userinfo.team_id},
            ]
        )
        workflow_publish_time = {}
        workflow_publish_creator = {}
        for workflow_item in workflow_info:
            workflow_publish_time[workflow_item['app_id']] = workflow_item['published_time']
            workflow_publish_creator[workflow_item['app_id']] = workflow_item['nickname']

        skill_model = CustomTools()
        skill_info = skill_model.select(
            columns=[
                'id as skill_id', 'app_id', 'published_time', 'users.nickname'
            ],
            joins=[
                ["left", "users", "users.id = custom_tools.user_id"],
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "publish_status", "value": 1},
                {"column": "team_id", "value": userinfo.team_id},
            ]
        )
        skill_publish_time = {}
        skill_publish_creator = {}
        skill_ids = {}
        for skill_item in skill_info:
            skill_publish_time[skill_item['app_id']] = skill_item['published_time']
            skill_publish_creator[skill_item['app_id']] = skill_item['nickname']
            skill_ids[skill_item['app_id']] = skill_item['skill_id']

        datasets_model = Datasets()
        datasets = datasets_model.select(
            columns=[
                'app_id', 'users.nickname'
            ],
            joins=[
                ["left", "users", "users.id = datasets.user_id"],
            ],
            conditions=[
                {"column": "status", "op": "in", "value": [1, 2]},
                {"column": "team_id", "value": userinfo.team_id},
            ]
        )

        datasets_publish_creator = {}
        for datasets_item in datasets:
            datasets_publish_creator[datasets_item['app_id']] = datasets_item['nickname']

        for item in request['list']:
            if item['mode'] == 1:
                item['agent_id'] = agent_ids.get(item['app_id'])
                item['published_time'] = agent_publish_time[item['app_id']]
                item['published_creator'] = agent_publish_creator[item['app_id']]
            elif item['mode'] == 2:
                item['published_time'] = workflow_publish_time[item['app_id']]
                item['published_creator'] = workflow_publish_creator[item['app_id']]
            elif item['mode'] == 3:
                item['published_time'] = None
                item['published_creator'] = datasets_publish_creator[item['app_id']]
            elif item['mode'] == 4:
                item['skill_id'] = skill_ids.get(item['app_id'])
                item['published_time'] = skill_publish_time.get(item['app_id'])
                item['published_creator'] = skill_publish_creator.get(item['app_id'])
            else:
                item['published_time'] = skill_publish_time[item['app_id']]
                item['published_creator'] = skill_publish_creator[item['app_id']]

    return response_success(request)

@router.post("/apps_create", response_model = ResAppsBaseCreateSchema)
async def apps_base_create(data:ReqAppBaseCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Create a new app with specified attributes.

    This endpoint facilitates the creation of a app, allowing configuration of various settings such as name, description, mode, icon, and icon_background through the provided schema. The mode parameter specifies the type of application.

    Parameters:
    - app_request (ReqAppBaseCreateSchema): A schema containing all the necessary information to create a app, including name, description, icon, icon_background, and mode. Required.
    - userinfo (TokenData): Information about the current user, provided through dependency injection. Required.

    Returns:
    - A response object indicating the success of the operation and containing the ID of the created app, formatted according to the ResAppsBaseCreateSchema model.

    Raises:
    - HTTPException: If any of the required parameters are missing or invalid, or if the user is not authenticated.
    """
    data = data.dict(exclude_unset=True)
    name = data['name']
    mode = data['mode']
    description = data['description']
    avatar = data.get('avatar', None)
    icon = data['icon']
    icon_background = data['icon_background']
    temporary_chatroom_id = data.get('temporary_chatroom_id', 0)

    if not name:
        return response_error(get_language_content("name_is_required"))
    if mode not in [1,2,3,4]:
        return response_error(get_language_content("mode_can_only_input"))
    if not avatar and not icon:
        return response_error(get_language_content("avatar_or_icon_required"))

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    team_id = userinfo.team_id
    uid = userinfo.uid
    team_type = Teams().get_team_type_by_id(team_id)
    if team_type == 2:
        return response_error(get_language_content("the_current_user_does_not_have_permission"))

    user_info = get_uid_user_info(uid)
    if user_info['role']!=1:
        return_status = Roles().check_role_deletable(user_info['role_id'],mode)
        if not return_status:
            return response_error(get_language_content("the_current_user_does_not_have_permission"))

    if avatar and avatar.startswith('upload_files/'):
        avatar = avatar.split('upload_files/')[-1]
    if avatar and avatar.startswith(('http://', 'https://')):
        avatar = avatar.split('/upload/')[-1]
    if mode == 3:
        publish_status =1
    else:
        publish_status =0

    # create app
    apps_data = {
        "team_id": team_id,
        "user_id": uid,
        "name": name,
        "icon": icon,
        "avatar": avatar,
        "icon_background": icon_background,
        "description": description,
        "mode": mode,
        "publish_status": publish_status,
        "created_time": current_time,
        "updated_time": current_time
    }
    app_model = Apps()
    app_id = app_model.insert(apps_data)
    if not app_id:
        return response_error(get_language_content("apps_insert_error"))

    if mode == 1:
        # create agent
        agents_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": app_id,
            "created_time": current_time,
            "updated_time": current_time
        }
        agent_model = Agents()
        agent_id = agent_model.insert(agents_data)
        if not agent_id:
            return response_error(get_language_content("agents_insert_error"))

    if mode == 2:
        # create workflow
        workflow_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": app_id,
            "created_time": current_time,
            "updated_time": current_time
        }
        workflow_model= Workflows()
        workflow_id = workflow_model.insert(workflow_data)
        if not workflow_id:
            return response_error(get_language_content("workflow_insert_error"))

    if mode == 3:
        try:
            embeddings_config_id = Models().get_model_by_type(2, team_id, 1, uid)['model_config_id']
        except AssertionError as e:
            msg = str(e)
            logger.info('create_dataset: %s desc: Request model %s, Current user id %s', msg, uid)
            return response_error(msg)
        collection_name = DatasetManagement.create_dataset(embeddings_config_id)
        retriever_config_dict = {item['key']: item['value'] for item in retriever_config}
        # create database
        database_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": app_id,
            "collection_name":collection_name,
            "embedding_model_config_id":embeddings_config_id,
            "retriever_config":retriever_config_dict,
            "temporary_chatroom_id": temporary_chatroom_id,
            "created_time": current_time,
            "updated_time": current_time,
            "temporary_chatroom_id": temporary_chatroom_id
        }

        datasets_model= Datasets()
        database_id = datasets_model.insert(database_data)
        if not database_id:
            return response_error(get_language_content("database_insert_error"))

    if mode ==4:
        # create skill
        skill_data = {
            "team_id": team_id,
            "user_id": uid,
            "app_id": app_id,
            "created_time": current_time,
            "updated_time": current_time
        }
        skill_model = CustomTools()
        skill_id = skill_model.insert(skill_data)
        if not skill_id:
            return response_error(get_language_content("skill_insert_error"))


    return response_success({'app_id':app_id},get_language_content("apps_insert_success"))

@router.put("/app_update/{app_id}", response_model = ResAppsBaseCreateSchema)
async def agent_base_update(app_id:int,data:ReqAppBaseCreateSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Update base app data based on parameters

    :param app_id: app id.
    :param name: app name.
    :param description: description.
    :param icon: incn
    :param icon_background: icon_background
    :return: A dictionary representing.
    """
    data = data.dict(exclude_unset=True)
    name = data['name']
    description = data['description']
    avatar = data.get('avatar', None)
    icon = data['icon']
    icon_background = data['icon_background']

    team_id = userinfo.team_id
    team_type = Teams().get_team_type_by_id(team_id)
    if team_type == 2:
        return response_error(get_language_content("the_current_user_does_not_have_permission"))
    uid =  userinfo.uid
    user_info = get_uid_user_info(uid)
    if user_info['role']!=1:
        app_model = Apps()
        appdata_mode = app_model.select_one(
            columns=[
                'mode'
            ],
            conditions=[

                {"column": "id", "value": app_id},
            ]
        )
        return_status = Roles().check_role_deletable(user_info['role_id'],appdata_mode['mode'])
        if not return_status:
            return response_error(get_language_content("the_current_user_does_not_have_permission"))

    if app_id <= 0:
        return response_error(get_language_content("app_id_is_required"))
    if not name:
        return response_error(get_language_content("name_is_required"))
    if not avatar and not icon:
        return response_error(get_language_content("avatar_or_icon_required"))
    if avatar and avatar.startswith('upload_files/'):
        avatar = avatar.split('upload_files/')[-1]
    if avatar and avatar.startswith(('http://', 'https://')):
        avatar = avatar.split('/upload/')[-1]

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    apps_data = {
        "name": name,
        "description": description,
        "icon": icon,
        "avatar": avatar,
        "icon_background":icon_background,
        "updated_time": current_time
    }

    app_model = Apps()
    appdata = app_model.select_one(
        columns=[
             'user_id'
        ],
        conditions=[

            {"column": "id", "value": app_id},
        ]
    )
    if userinfo.uid != appdata['user_id']:
        return response_error(get_language_content("no_modification_permission"))

    apps_update_res = app_model.update({"column": "id", "value": app_id}, apps_data)
    if not apps_update_res:
        return response_error(get_language_content("app_update_error"))


    return response_success({},get_language_content("app_update_sucess"))


