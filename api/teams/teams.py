import json
import hashlib
from datetime import datetime
from fastapi import APIRouter, Body, Depends, Query
from api.schema.teams import TeamCreateRequest, TeamUpdateRequest, TeamStatusUpdateRequest
from api.utils.common import *
from api.utils.jwt import *
from core.database.models.teams import Teams
from core.database.models.users import Users
from core.database.models.user_team_relations import UserTeamRelations
from core.database.models.model_configurations import ModelConfigurations
from languages import get_language_content

router = APIRouter()


# Endpoint to create a new team
@router.post("/team")
async def create_team(
    request: TeamCreateRequest,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Create a new team with associated administrator user and model configurations.
    
    Args:
        request: Team creation request containing name, account, password and optional config
        userinfo: Current user information (used to get tenant_id)
        
    Returns:
        JSON response with created team information
    """
    try:
        # Validate current user's tenant_id
        if not userinfo.tenant_id or userinfo.tenant_id == 0:
            return response_error(get_language_content("team_tenant_id_required"))
        
        # Validate team name
        if not request.name or request.name.strip() == "":
            return response_error(get_language_content("team_name_required"))
        
        # Validate account
        if not request.account or request.account.strip() == "":
            return response_error(get_language_content("team_account_required"))
        
        # Validate password
        if not request.password or request.password.strip() == "":
            return response_error(get_language_content("team_password_required"))
        
        # Check if account already exists
        existing_user = Users().select_one(
            columns=['id'],
            conditions=[
                {'column': 'email', 'value': request.account.strip()},
                {'column': 'status', 'value': 1}
            ]
        )
        
        if existing_user:
            return response_error(get_language_content("team_account_exists"))
        
        # Validate config if provided
        if request.config is not None and request.config:
            try:
                config_str = json.dumps(request.config)
            except Exception:
                return response_error(get_language_content("team_config_invalid"))
        else:
            config_str = None
        
        current_time = datetime.now()
        
        # 1. Insert into teams table
        team_data = {
            'name': request.name.strip(),
            'tenant_id': 0,
            'type': 1,
            'created_time': current_time,
            'status': 1
        }
        
        # Only add config if it has a value
        if config_str is not None:
            team_data['config'] = config_str
        
        team_id = Teams().insert(team_data)
        
        if not team_id:
            return response_error(get_language_content("team_create_failed"))
        
        # 2. Create administrator user and insert into users table
        # Generate password salt (using timestamp as salt, consistent with auth.py validation logic)
        password_salt = str(int(current_time.timestamp()))
        
        # Use the same encryption method as fake_hash_password in auth.py: MD5(MD5(password) + salt)
        password_with_salt = hashlib.md5(
            (hashlib.md5(request.password.encode()).hexdigest() + password_salt).encode()
        ).hexdigest()
        
        user_data = {
            'team_id': team_id,
            'role': 1,
            'role_id': 1,
            'tenant_id': userinfo.tenant_id,
            'inviter_id': 0,
            'email': request.account.strip(),
            'nickname': 'administrator',
            'password': password_with_salt,
            'password_salt': password_salt,
            'created_time': current_time,
            'status': 1,
            'language': 'en'
        }
        user_id = Users().insert(user_data)
        
        if not user_id:
            return response_error(get_language_content("team_create_failed"))
        
        # 3. Insert into user_team_relations table
        relation_data = {
            'user_id': user_id,
            'team_id': team_id,
            'role': 1,  # Admin role
            'inviter_id': 0,
            'created_time': current_time
        }
        relation_id = UserTeamRelations().insert(relation_data)
        
        if not relation_id:
            return response_error(get_language_content("team_create_failed"))
        
        # 4. Copy model configurations from team_id=1
        model_configs = ModelConfigurations().select(
            columns=['model_id', 'config', 'default_used', 'sort_order'],
            conditions=[
                {'column': 'team_id', 'value': 1},
                {'column': 'status', 'value': 1}
            ]
        )
        
        if model_configs:
            for config in model_configs:
                model_config_data = {
                    'team_id': team_id,
                    'model_id': config['model_id'],
                    'config': config['config'],
                    'default_used': config['default_used'],
                    'sort_order': config['sort_order'],
                    'created_time': current_time,
                    'updated_time': None,
                    'status': 1
                }
                ModelConfigurations().insert(model_config_data)
        
        return response_success({'team_id': team_id}, get_language_content("team_create_success"))
        
    except Exception as e:
        print(f"Failed to create team: {e}")
        return response_error(f"{get_language_content('team_create_failed')}: {str(e)}")


# Endpoint to update team information
@router.put("/team")
async def update_team(
    request: TeamUpdateRequest,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Update team information (name and/or config).
    
    Args:
        request: Team update request containing team_id and optional name and config
        userinfo: Current user information
        
    Returns:
        JSON response with update status
    """
    try:
        # Check if team exists
        team = Teams().select_one(
            columns=['id', 'tenant_id'],
            conditions=[
                {'column': 'id', 'value': request.team_id},
                {'column': 'status', 'value': 1}
            ]
        )
        
        if not team:
            return response_error(get_language_content("team_not_found"))
        
        # Prepare update data
        update_data = {}
        
        if request.name is not None:
            if request.name.strip() == "":
                return response_error(get_language_content("team_name_required"))
            update_data['name'] = request.name.strip()
        
        if request.config is not None:
            if request.config:
                try:
                    update_data['config'] = json.dumps(request.config)
                except Exception:
                    return response_error(get_language_content("team_config_invalid"))
            # If config is empty dict {}, don't update it (keep existing value)
            # To clear config, client should send null in JSON, not empty object
        
        if not update_data:
            return response_error(get_language_content("team_update_failed"))
        
        update_data['updated_time'] = datetime.now()
        
        # Update team
        Teams().update(
            [{'column': 'id', 'value': request.team_id}],
            update_data
        )
        
        return response_success({}, get_language_content("team_update_success"))
        
    except Exception as e:
        print(f"Failed to update team: {e}")
        return response_error(f"{get_language_content('team_update_failed')}: {str(e)}")


# Endpoint to update team status
@router.post("/team/status")
async def update_team_status(
    request: TeamStatusUpdateRequest,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Update team status.
    
    Args:
        request: Team status update request containing team_id and status
        userinfo: Current user information
        
    Returns:
        JSON response with operation status
    """
    try:
        # Validate current user's tenant_id
        if not userinfo.tenant_id or userinfo.tenant_id == 0:
            return response_error(get_language_content("team_tenant_id_required"))
        
        # Validate status
        if request.status not in [1, 2, 3]:
            return response_error(get_language_content("team_invalid_status"))
        
        # Check if team exists
        team = Teams().select_one(
            columns=['id', 'tenant_id'],
            conditions=[
                {'column': 'id', 'value': request.team_id}
            ]
        )
        
        if not team:
            return response_error(get_language_content("team_not_found"))
        
        # Validate tenant_id matches
        if team['tenant_id'] != userinfo.tenant_id:
            return response_error(get_language_content("team_tenant_mismatch"))
        
        # Update team status
        Teams().update(
            [{'column': 'id', 'value': request.team_id}],
            {
                'status': request.status,
                'updated_time': datetime.now()
            }
        )
        
        return response_success({}, get_language_content("team_status_updated_success"))
        
    except Exception as e:
        print(f"Failed to update team status: {e}")
        return response_error(f"{get_language_content('team_status_update_failed')}: {str(e)}")


# Endpoint to get team details
@router.get("/team/{team_id}")
async def get_team(
    team_id: int,
    userinfo: TokenData = Depends(get_current_user)
):
    """
    Get detailed information for a specific team.
    
    Args:
        team_id: Team ID to retrieve
        userinfo: Current user information
        
    Returns:
        JSON response with team details
    """
    try:
        # Validate current user's tenant_id
        if not userinfo.tenant_id or userinfo.tenant_id == 0:
            return response_error(get_language_content("team_tenant_id_required"))
        
        # Get team information
        team = Teams().select_one(
            columns=['id', 'name', 'tenant_id', 'type', 'config', 'created_time', 'updated_time', 'status'],
            conditions=[
                {'column': 'id', 'value': team_id}
            ]
        )
        
        if not team:
            return response_error(get_language_content("team_not_found"))
        
        # Validate tenant_id matches
        if team['tenant_id'] != userinfo.tenant_id:
            return response_error(get_language_content("team_tenant_mismatch"))
        
        # Parse config if it exists
        if team['config']:
            try:
                team['config'] = json.loads(team['config'])
            except Exception:
                team['config'] = None
        
        return response_success(team)
        
    except Exception as e:
        print(f"Failed to get team details: {e}")
        return response_error(f"Failed to get team details: {str(e)}")
