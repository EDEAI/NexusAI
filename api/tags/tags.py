from fastapi import APIRouter, Depends
from core.helper import get_tags_mode_by_app_modes
from api.schema.tags import (
    CreateTagRequest, UpdateTagRequest, TagResponse, 
    CreateTagBindingRequest, TagsListResponse
)
from api.utils.common import response_error, response_success
from api.utils.jwt import get_current_user, TokenData
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

@router.get("/tags", response_model=TagsListResponse)
async def list_tags(mode: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Get a list of tags.

    Parameters:
    - mode: int, mode of the tags
    - userinfo: TokenData, user information for authentication

    Returns:
    - Success response with the list of tags
    """
    if mode == 0:
        tag_data = tag.get_tag_list(user_id=userinfo.uid, team_id=userinfo.team_id)
    else:
        mode = get_tags_mode_by_app_modes(mode)
        tag_data = tag.get_tag_list(user_id=userinfo.uid, team_id=userinfo.team_id, mode=mode[0])

    # Calculate reference count for each tag
    for tag_item in tag_data:
        tag_id = tag_item['id']
        total_count = tag_bindings.get_tag_binding_by_count_id(tag_id=tag_id)
        tag_item['reference_count'] = total_count if total_count else 0

    return response_success(tag_data)

@router.post("/tags", response_model=TagResponse)
async def create_tag(request: CreateTagRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Create a new tag.

    Parameters:
    - request: CreateTagRequest, containing team_id, mode, and name
    - userinfo: TokenData, user information for authentication

    Returns:
    - Success response with the created tag data
    """
    team_info = teams.select_one(columns="*", conditions=[
        {"column": "id", "value": userinfo.team_id},
        {"column": "status", "value": 1}
    ])

    if not team_info:
        return response_error(get_language_content('team_id_not_found'))

    _mode = get_tags_mode_by_app_modes(request.mode)
    tag_id = tag.insert_tag(team_id=userinfo.team_id, user_id=userinfo.uid, mode=_mode[0], name=request.name)
    new_tag = tag.get_tag_by_id(tag_id=tag_id, user_id=userinfo.uid, team_id=userinfo.team_id)
    return response_success(new_tag)

@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, request: UpdateTagRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Update an existing tag.

    Parameters:
    - tag_id: int, path parameter for tag id
    - request: UpdateTagRequest, containing new name
    - userinfo: TokenData, user information for authentication

    Returns:
    - Success response
    """
    # Check if tag exists and is active
    tag_info = tag.get_tag_by_id(tag_id, userinfo.uid, userinfo.team_id)
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))
    if tag.update_tag(tag_id, request.name, userinfo.team_id, userinfo.uid):
        return response_success(detail=get_language_content('tag_update_success'))
    else:
        return response_error(get_language_content('tag_update_failed'))

@router.delete("/tags/{tag_id}", response_model=TagResponse)
async def delete_tag(tag_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete a tag (soft delete by updating status and removing bindings).

    Parameters:
    - tag_id: int, path parameter for tag id
    - userinfo: TokenData, user information for authentication

    Returns:
    - Success response
    """
    # Check if tag exists and is active
    tag_info = tag.get_tag_by_id(tag_id, userinfo.uid, userinfo.team_id)
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))

    # Remove all bindings related to the tag
    tag_bindings.delete([
        {"column": "tag_id", "value": tag_id}
    ])

    # Soft delete the tag by updating its status
    tag.update(
        [{'column': 'id', 'value': tag_id}, {'column': 'team_id', 'value': userinfo.team_id}, {'column': 'user_id', 'value': userinfo.uid}],
        {'status': 3}  # 3 represents deleted status
    )

    return response_success(detail=get_language_content('tag_delete_success'))

@router.post("/tags_bindings", response_model=TagResponse)
async def bind_tags(request: CreateTagBindingRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Bind multiple tags to multiple apps.
    """
    tag_ids = request.tag_ids
    app_ids = request.app_ids

    if not app_ids:
        return response_error(get_language_content('app_id_is_required'))

    # Check if apps exist
    app_data = apps.select(columns="*", conditions=[{"column": "id", "op": "in", "value": app_ids}])
    if not app_data:
        return response_error(get_language_content('app_id_is_required'))

    if tag_ids:
        # Check if tags exist
        tag_data = tag.select(columns="*", conditions=[
            {"column": "id", "op": "in", "value": tag_ids},
            {"column": "status", "value": 1},
            {"column": "team_id", "value": userinfo.team_id},
            {"column": "user_id", "value": userinfo.uid}
        ])
        if not tag_data:
            return response_error(get_language_content('tag_id_not_found'))

    # Use the new batch update method
    if tag_bindings.batch_update_bindings(app_ids, tag_ids):
        return response_success(detail=get_language_content('tag_binding_create_success'))
    else:
        return response_error(get_language_content('tag_binding_create_failed'))
