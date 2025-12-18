from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any

from core.database.models.api_keys import ApiKeys
from core.database.models.apps import Apps
from api.utils.common import response_success, response_error
from api.utils.jwt import get_current_user
from api.schema.api_key import (
    ResApiKeyListSchema,
    ResCreateApiKeySchema,
    ResDeleteApiKeySchema
)
from api.utils.jwt import TokenData

router = APIRouter()


@router.post('/create', response_model=ResCreateApiKeySchema, summary="Create a new API key for an app")
async def create_api_key(
    app_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Create a new API key for an app.
    
    Parameters:
    - app_id: The ID of the app to create the API key for.
    - current_user: The current authenticated user.
    
    Returns:
    - The created API key information.
    
    Raises:
    - HTTPException: If the app doesn't exist or doesn't belong to the user.
    """
    # Verify that the app exists and belongs to the user
    app = Apps().select_one(
        columns=['id', 'user_id'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'user_id', 'value': current_user.uid},
            {'column': 'status', 'value': 1}
        ]
    )
    
    if not app:
        return response_error("App not found or you don't have permission to access this app")
    
    # Create the API key
    api_keys_model = ApiKeys()
    api_key_data = api_keys_model.create_api_key(app_id, current_user.uid)
    
    # Return the response
    return response_success({
        'id': api_key_data['id'],
        'key': api_key_data['key'],
        'app_id': api_key_data['app_id'],
        'user_id': api_key_data['user_id'],
        'status': api_key_data['status'],
        'created_time': api_key_data['created_time']
    })


@router.get('/list', response_model=ResApiKeyListSchema, summary="Get all API keys for an app")
async def get_api_keys(
    app_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Get all API keys for an app created by the current user.
    
    Parameters:
    - app_id: The ID of the app to get API keys for.
    - current_user: The current authenticated user.
    
    Returns:
    - A list of API keys for the app.
    
    Raises:
    - HTTPException: If the app doesn't exist or doesn't belong to the user.
    """
    # Verify that the app exists and belongs to the user
    app = Apps().select_one(
        columns=['id', 'user_id'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'user_id', 'value': current_user.uid},
            {'column': 'status', 'value': 1}
        ]
    )
    
    if not app:
        return response_error("App not found or you don't have permission to access this app")
    
    # Get all API keys for the app
    api_keys_model = ApiKeys()
    api_keys = api_keys_model.get_api_keys_by_app_and_user(app_id, current_user.uid)
    
    # Return the response
    return response_success({
        'list': api_keys,
        'total_count': len(api_keys)
    })


@router.delete('/{key_id}', response_model=ResDeleteApiKeySchema, summary="Delete an API key")
async def delete_api_key(
    key_id: int,
    app_id: int,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Soft delete an API key by setting its status to 0.
    
    Parameters:
    - key_id: The ID of the API key to delete.
    - app_id: The ID of the app the API key belongs to.
    - current_user: The current authenticated user.
    
    Returns:
    - Success message.
    
    Raises:
    - HTTPException: If the API key doesn't exist or doesn't belong to the user.
    """
    # Verify that the app exists and belongs to the user
    app = Apps().select_one(
        columns=['id', 'user_id'],
        conditions=[
            {'column': 'id', 'value': app_id},
            {'column': 'user_id', 'value': current_user.uid},
            {'column': 'status', 'value': 1}
        ]
    )
    
    if not app:
        return response_error("App not found or you don't have permission to access this app")
    
    # Soft delete the API key (set status to 0)
    api_keys_model = ApiKeys()
    success = api_keys_model.delete_api_key(key_id, current_user.uid)
    
    if not success:
        return response_error("API key not found or you don't have permission to delete it")
    
    # Return the response
    return response_success({"message": "API key deleted successfully"})