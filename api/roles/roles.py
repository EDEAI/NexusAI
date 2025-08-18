from fastapi import APIRouter
from typing import Optional
from core.database.models.roles import Roles
from core.database.models.permissions import Permission
from core.database.models.role_permission import RolePermission
from api.schema.user_role import *
from api.utils.common import *
from api.utils.jwt import *
import json
import sys, os
from time import time
from datetime import datetime
from languages import get_language_content
router = APIRouter()

@router.get("/", response_model=RolesListResponse, summary="Get Roles List")
async def roles_list(page: int = 1, page_size: int = 10, status: int = 1, name: str = "", userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve a list of roles with pagination and optional name filtering.
    Args:
        page (int): Current page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10.
        name (str): Optional role name for fuzzy search filtering.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Standard response containing role list, formatted according to RoleListResponse model.
    Raises:
        HTTPException: When query execution fails.
    """
    team_id = userinfo.team_id
    roles = Roles()

    if status not in [1, 2]:
        return response_error(get_language_content("roles_status_only_one_or_two"))
    result = roles.get_roles_list(page, page_size, status, name, team_id)
    return response_success(result)


@router.get("/permission_list", response_model=PermissionListResponse, summary="Get Permission List")
async def permission_list(page: int = 1, page_size: int = 10, status: int = 1, name: str = "", userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve a list of permissions with pagination and optional name filtering.
    Args:
        page (int): Current page number for pagination. Default is 1.
        page_size (int): Number of items per page. Default is 10.
        status (int): Status filter (1 for pagination, 2 for all records). Default is 1.
        name (str): Optional permission name for fuzzy search filtering.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Standard response containing permission list, formatted according to PermissionListResponse model.
    Raises:
        HTTPException: When query execution fails.
    """
    permission = Permission()
    uid = userinfo.uid
    
    if status not in [1, 2]:
        return response_error(get_language_content("permission_status_only_one_or_two"))
    
    result = permission.get_permission_list(page, page_size, uid, name, status)
    return response_success(result)


@router.post("/create_role", response_model=CreateRole, summary="Create Role")
async def create_role(role_request: CreateRoleSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Create a new role and its role-permission relations.
    Args:
        role_request (CreateRoleSchema): Request body containing role name, description, and permission list.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Dict with result info, including the new role_id.
    """
    data = role_request.dict(exclude_unset=True)
    team_id = userinfo.team_id
    perm_model = Permission()
    if not data['list'] or not perm_model.check_permissions_exist(data['list']):
        return response_error(get_language_content("Permission_does_not_exist"))
    # Create role
    roles = Roles()
    role_id = roles.insert({
        "name": data['name'],
        "team_id": team_id,
        "description": data['description'],
        "created_at": datetime.now()
    })

    # Create role-permission relations
    role_perm_model = RolePermission()
    for pid in data['list']:
        role_perm_model.insert({
            "role_id": role_id,
            "permission_id": pid
        })
    return response_success({'role_id': role_id})


@router.put("/update_role/{role_id}", response_model=CreateRole, summary="Update Role")
async def update_role(role_id: int, role_request: CreateRoleSchema, userinfo: TokenData = Depends(get_current_user)):
    """
    Update role and its role-permission relations.
    Args:
        role_id (int): The ID of the role to update.
        role_request (CreateRoleSchema): Request body containing updated role name, description, and permission list.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Dict with result info, including the updated role_id.
    """
    roles = Roles()
    role_info = roles.get_role_by_id(role_id)
    if not role_info:
        return response_error(get_language_content("Permission_does_not_exist"))
    # Check if tag exists and is active
    data = role_request.dict(exclude_unset=True)
    perm_model = Permission()
    if not data['list'] or not perm_model.check_permissions_exist(data['list']):
        return response_error(get_language_content("Permission_does_not_exist"))
    # Update role
    roles.update(
        data={
            "name": data['name'],
            "description": data['description'],
            "updated_at": datetime.now()
        },
        conditions=[
            {'column': 'id', 'value': role_id}
        ]
    )

    # Handle role-permission relations
    role_perm_model = RolePermission()
    # Get current permission_ids for this role
    old_permission_ids = set(role_perm_model.get_permission_ids_by_role_id(role_id))
    new_permission_ids = set(data['list'])

    # Permissions to delete
    to_delete = old_permission_ids - new_permission_ids
    # Permissions to add
    to_add = new_permission_ids - old_permission_ids

    # Delete redundant permissions
    for pid in to_delete:
        role_perm_model.delete([
            {"column": "role_id", "value": role_id},
            {"column": "permission_id", "value": pid}
        ])
    # Add new permissions
    for pid in to_add:
        role_perm_model.insert({
            "role_id": role_id,
            "permission_id": pid
        })
    return response_success({'role_id': role_id})


@router.delete("/{role_id}", response_model=OperationResponse, summary="Delete the Role")
async def delete_chatroom(role_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Delete a role by its ID (soft delete).
    Args:
        role_id (int): The unique identifier of the role to be deleted.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Dict with result info, including a success message.
    Raises:
        HTTPException: If the role ID is missing, the user is not authenticated, or the role does not exist.
    """
    if not role_id:
        return response_error(get_language_content("role_id_is_required"))

    roles = Roles()
    role_info = roles.get_role_by_id(role_id)
    if not role_info:
        return response_error(get_language_content("Permission_does_not_exist"))

    roles.update(
        data={
            "status": 3,
            "updated_at": datetime.now()
        },
        conditions=[
            {'column': 'id', 'value': role_id}
        ]
    )
    return response_success({'msg': get_language_content("role_delete_success")})


@router.get("/role_detail", response_model=RoleDetailResponse, summary="Get Role Detail")
async def get_role_detail(role_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Get role details including associated permissions.
    Args:
        role_id (int): The ID of the role to retrieve.
        userinfo (TokenData): Current user information, obtained through authentication.
    Returns:
        Dict with role details including permissions list.
    Raises:
        HTTPException: When role is not found or query execution fails.
    """
    uid = userinfo.uid
    
    if not role_id or role_id <= 0:
        return response_error(get_language_content("invalid_role_id"))
    
    roles = Roles()
    role_detail = roles.get_role_detail_with_permissions(role_id, uid)
    
    if not role_detail:
        return response_error(get_language_content("role_not_found"))

    if role_detail.get('built_in') == 1:
        # For built-in roles, the name field contains the language key
        role_key = role_detail['name']  # e.g., 'comprehensive_administrator'
        # Translate role name
        role_detail['name'] = get_language_content(role_key)
        # Set role description using the corresponding _desc key
        role_detail['description'] = get_language_content(f"{role_key}_desc")
    
    return response_success(role_detail)
