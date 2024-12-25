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
        conditions = [
            {"column": "team_id", "value": userinfo.team_id},
            {"column": "user_id", "value": userinfo.uid},
            {"column": "status", "value": 1},
        ]
    else:
        mode = get_tags_mode_by_app_modes(mode)
        conditions = [
            {"column": "team_id", "value": userinfo.team_id},
            {"column": "user_id", "value": userinfo.uid},
            {"column": "mode", "value": mode[0]},
            {"column": "status", "value": 1}
        ]
    tag_data = tag.select(columns="*", conditions=conditions, order_by="created_time DESC")

    # Calculate reference count for each tag
    for tag_item in tag_data:
        tag_id = tag_item['id']
        total_count = tag_bindings.select_one(
            aggregates={"id": "count"},
            conditions=[{"column": "tag_id", "value": tag_id}]
        )['count_id']
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

    if team_info:
        _mode = get_tags_mode_by_app_modes(request.mode)
        tag_id = tag.insert({
            'team_id': userinfo.team_id,
            'user_id': userinfo.uid,
            'mode': _mode[0],
            'name': request.name,
        })
        new_tag = tag.select_one(columns={'id', 'team_id', 'user_id', 'name'}, conditions=[
            {"column": "id", "value": tag_id}
        ])
        return response_success(new_tag)
    else:
        return response_error(get_language_content('team_id_not_found'))

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
    tag.update(
        [{'column': 'id', 'value': tag_id}],
        {'name': request.name}
    )
    return response_success(detail=get_language_content('tag_update_success'))

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
        [{'column': 'id', 'value': tag_id}],
        {'status': 3}  # 3 represents deleted status
    )

    return response_success(detail=get_language_content('tag_delete_success'))

@router.post("/tags_bindings", response_model=TagResponse)
async def bind_tags(request: CreateTagBindingRequest, userinfo: TokenData = Depends(get_current_user)):
    """
    Bind multiple tags to multiple apps. An app can have multiple tags and a tag can be bound to multiple apps.

    Parameters:
    - request: CreateTagBindingRequest, containing tag_ids and app_ids
    - userinfo: TokenData, user information for authentication

    Returns:
    - Success response with binding status
    """
    tag_ids = request.tag_ids
    app_ids = request.app_ids

    if not tag_ids:
        return response_error(get_language_content('tag_id_not_found'))
    if not app_ids:
        return response_error(get_language_content('app_id_is_required'))

    # Check if apps exist
    app_data = apps.select(columns="*", conditions=[{"column": "id", "op": "in", "value": app_ids}])
    if not app_data:
        return response_error(get_language_content('app_id_is_required'))

    # Check if tags exist and are active
    tag_info = tag.select(columns="*", conditions=[
        {"column": "id", "op": "in", "value": tag_ids},
        {"column": "team_id", "value": userinfo.team_id},
        {"column": "user_id", "value": userinfo.uid},
        {'column': 'status', 'value': 1}
    ])
    if not tag_info:
        return response_error(get_language_content('tag_id_not_found'))

    # Get all existing bindings for the given app_ids
    existing_bindings = tag_bindings.select(columns=["tag_id", "app_id"], conditions=[
        {"column": "app_id", "op": "in", "value": app_ids}
    ])
    existing_bindings_dict = {}
    for binding in existing_bindings:
        if binding['app_id'] not in existing_bindings_dict:
            existing_bindings_dict[binding['app_id']] = set()
        existing_bindings_dict[binding['app_id']].add(binding['tag_id'])

    for app_id in app_ids:
        existing_tag_ids = existing_bindings_dict.get(app_id, set())

        # Determine tags to add and tags to remove
        tags_to_add = set(tag_ids) - existing_tag_ids
        tags_to_remove = existing_tag_ids - set(tag_ids)

        # Remove bindings that are no longer needed
        for tag_id in tags_to_remove:
            tag_bindings.delete([
                {"column": "tag_id", "value": tag_id},
                {"column": "app_id", "value": app_id}
            ])

        # Add new bindings
        for tag_id in tags_to_add:
            tag_bindings.insert({
                'tag_id': tag_id,
                'app_id': app_id
            })

    return response_success(detail=get_language_content('tag_binding_create_success'))
