from core.helper import get_tags_mode_by_app_modes
from fastapi import APIRouter, Depends
from api.schema.tags import CreateTagRequest, UpdateTagRequest, DeleteTagRequest, TagResponse, CreateTagBindingRequest, \
    DeleteTagBindingRequest, TageListRequest, TagListResponse
from api.utils.common import response_error, response_success
from api.utils.jwt import *
from core.database.models.tags import Tags
from core.database.models.apps import Apps
from core.database.models.tag_bindings import TagBindings
from core.database.models.teams import Teams
from languages import get_language_content

# Create a new APIRouter instance
router = APIRouter()
tag = Tags()
apps = Apps()
tag_bindings = TagBindings()
teams = Teams()


@router.post("/tag_list", response_model=TagListResponse)
async def tag_list(request: TageListRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Get a list of tags.

    Parameters:
    - request: TageListRequest containing team_id and mode
    - userinfo: TokenData for authentication

    Returns:
    - Success response with the list of tags
    """
    if request.mode == 0:
        conditions = [
            {"column": "team_id", "value": request.team_id},
            {"column": "status", "value": 1}
        ]
    else:
        conditions = [
            {"column": "team_id", "value": request.team_id},
            {"column": "mode", "value": request.mode},
            {"column": "status", "value": 1}
        ]
    tag_data = tag.select(columns="*", conditions=conditions)
    return response_success(tag_data)


@router.post("/tag_create", response_model=TagResponse)
async def create_tag(request: CreateTagRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Create a new tag.

    Parameters:
    - request: CreateTagRequest containing team_id, mode, and name
    - userinfo: TokenData for authentication

    Returns:
    - Success response with the created tag data
    """
    team_info = teams.select_one(columns="*", conditions=[
        {"column": "id", "value": request.team_id},
        {"column": "status", "value": 1}
    ])

    if team_info:
        _mode = get_tags_mode_by_app_modes(request.mode)
        tag.insert({
            'team_id': request.team_id,
            'mode': _mode,
            'name': request.name,
        })
        return response_success(detail=get_language_content('tag_create_success'))
    else:
        return response_error(get_language_content('team_id_not_found'))


@router.post("/tag_update", response_model=TagResponse)
async def update_tag(request: UpdateTagRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Update an existing tag.

    Parameters:
    - request: UpdateTagRequest containing tag_id and new name
    - userinfo: TokenData for authentication

    Returns:
    - Success response
    """
    # Check if tag exists and is active
    tag_info = tag.get_tag_by_id(request.tag_id)
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))
    tag.update(
        [{'column': 'id', 'value': request.tag_id}],
        {'name': request.name}
    )
    return response_success(detail=get_language_content('tag_update_success'))


@router.post("/tag_delete", response_model=TagResponse)
async def delete_tag(request: DeleteTagRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete a tag (soft delete by updating status).

    Parameters:
    - request: DeleteTagRequest containing tag id
    - userinfo: TokenData for authentication

    Returns:
    - Success response
    """
    # Check if tag exists and is active
    tag_info = tag.get_tag_by_id(request.tag_id)
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))
    tag.update(
        [{'column': 'id', 'value': request.tag_id}],
        {'status': 3}  # 3 represents deleted status
    )
    return response_success(detail=get_language_content('tag_delete_success'))


@router.post("/tag_bind", response_model=TagResponse)
async def bind_tag(request: CreateTagBindingRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Bind a tag to an app. An app can have multiple tags.

    Parameters:
    - request: CreateTagBindingRequest containing tag_id and app_id
    - userinfo: TokenData for authentication

    Returns:
    - Success response with binding status
    """
    tag_datas = request.tag_id
    if len(tag_datas) <= 0:
        return response_error(get_language_content('tag_id_not_found'))

    # Check if app exists
    app_data = apps.select_one(columns="*", conditions=[{"column": "id", "value": request.app_id}])
    if not app_data:
        return response_error(get_language_content('app_id_is_required'))

    # Check if tag exists and is active
    tag_info = tag.select(columns="*", conditions=[
        {"column": "id", "op": "in", "value": tag_datas},
        {'column': 'status', 'value': 1}
    ])
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))

    for tag_id in tag_datas:
        tag_bindings_data = tag_bindings.select(columns="*", conditions=[
            {"column": "tag_id", "value": tag_id},
            {"column": "app_id", "value": request.app_id},
        ])
        if not tag_bindings_data:
            # Create new binding
            tag_bindings.insert({
                'tag_id': tag_id,
                'app_id': request.app_id
            })
    return response_success(detail=get_language_content('tag_binding_create_success'))


@router.post("/tag_bindings_delete", response_model=TagResponse)
async def delete_tag_bindings(request: DeleteTagBindingRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete tag bindings.

    Parameters:
    - request: DeleteTagBindingRequest containing tag_id and app_id
    - userinfo: TokenData for authentication

    Returns:
    - Success response
    """
    tag_datas = request.tag_id
    if len(tag_datas) <= 0:
        return response_error(get_language_content('tag_id_not_found'))

    # Check if app exists
    app_data = apps.select_one(columns="*", conditions=[{"column": "id", "value": request.app_id}])
    if not app_data:
        return response_error(get_language_content('app_id_is_required'))

    # Check if tag exists and is active
    tag_info = tag.select(columns="*", conditions=[
        {"column": "id", "op": "in", "value": tag_datas},
        {'column': 'status', 'value': 1}
    ])
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))

    # Delete the bindings
    tag_bindings.delete([
        {"column": "tag_id", "op": "in", "value": tag_datas},
        {"column": "app_id", "value": request.app_id}
    ])

    return response_success(detail=get_language_content('tag_binding_delete_success'))


@router.post("/tag_binding_list", response_model=TagListResponse)
async def tag_binding_list(request: TageListRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Get a list of tags.

    Parameters:
    - request: TageListRequest containing team_id and mode
    - userinfo: TokenData for authentication

    Returns:
    - Success response with the list of tags
    """
    if request.mode == 0:
        conditions = [
            {"column": "team_id", "value": request.team_id},
            {"column": "status", "value": 1}
        ]
    else:
        conditions = [
            {"column": "team_id", "value": request.team_id},
            {"column": "mode", "value": request.mode},
            {"column": "status", "value": 1}
        ]
    tag_data = tag.select(columns="*", conditions=conditions)
    return response_success(tag_data)

