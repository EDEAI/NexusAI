from fastapi import APIRouter, Body, Depends, Query
from api.schema.tools import toolsResponse, PaginatedToolsResponse, PaginatedToolsData
from api.utils.common import *
from api.utils.jwt import *
from core.tool.provider.builtin_tool_provider import *
from core.database.models.tool_authorizations import ToolAuthorizations
from core.tool.provider.builtin_tool_provider import validate_credentials, BuiltinTool
import math
from typing import Optional, Union

router = APIRouter()


# Endpoint to retrieve the list of tools with their authorization status.
@router.get("/tools", response_model=Union[toolsResponse, PaginatedToolsResponse])
async def get_tools(
    userinfo: TokenData = Depends(get_current_user),
    page: Optional[int] = Query(None, ge=1, description="Page number (starts from 1)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Number of items per page (max 100)")
):
    try:
        # Fetch the available tool providers and their associated tools.
        tools = get_docker_sandbox_tools()
        
        # If no tools found, return empty response
        if not tools:
            if page is not None and page_size is not None:
                # Return paginated empty response
                paginated_data = PaginatedToolsData(
                    tools={},
                    total_count=0,
                    total_pages=0,
                    page=page,
                    page_size=page_size
                )
                return response_success(paginated_data.dict())
            else:
                # Return legacy empty response
                return response_success({})
        
        # Process tools and set authorization status
        processed_providers = {}
        for category_name, category_data in tools.items():
            if isinstance(category_data, dict):
                for provider_name, provider_data in category_data.items():
                    # Check if the tool provider requires credentials.
                    if 'credentials_for_provider' in provider_data and provider_data['credentials_for_provider']:
                        tool = ToolAuthorizations()
                        # Get the authorization status of the tool for the current user and team.
                        tool_result = tool.get_tool_info(user_id=userinfo.uid, team_id=userinfo.team_id, provider=provider_name, tool_category=category_name)
                        
                        if tool_result["status"] != 1:
                            provider_data['authorization_status'] = 2  # Unauthorized
                        else:
                            provider_data['authorization_status'] = 1  # Authorized
                    else:
                        # No authorization required for this tool provider.
                        provider_data['authorization_status'] = 3
                    
                    # Add provider to processed tools
                    processed_providers[provider_name] = provider_data
        
        # If pagination parameters are provided, return paginated response
        if page is not None and page_size is not None:
            # Convert to list for pagination
            provider_items = list(processed_providers.items())
            total_count = len(provider_items)
            total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0
            
            # Calculate start and end indices
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            # Get the current page items
            page_items = provider_items[start_index:end_index]
            page_providers = dict(page_items)
            
            # Create paginated response
            paginated_data = PaginatedToolsData(
                tools=page_providers,
                total_count=total_count,
                total_pages=total_pages,
                page=page,
                page_size=page_size
            )
            return response_success(paginated_data.dict())
        else:
            # Return legacy response format (all tools)
            return response_success(processed_providers)

    except Exception as e:
        print(f"Failed to fetch tools: {e}")
        return response_error(f"Failed to fetch tools: {str(e)}")


# Endpoint to update the credentials for a specific tool provider.
@router.put("/tools_authorization/{provider}")
async def skill_update(provider: str, tool_category: str = 't1', credentials: Dict[str, Any] = Body(...),
                       userinfo: TokenData = Depends(get_current_user)):
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        # Validate the provided credentials for the given provider.
        # if validate_credentials(provider, credentials):
        tool = ToolAuthorizations()
        # Retrieve current authorization status for the tool.
        tool_result = tool.get_tool_info(user_id=user_id, team_id=team_id, provider=provider,tool_category=tool_category)
        # If the tool is not authorized, insert new credentials.
        if tool_result["status"] != 1:
            insert_data = {
                'team_id': team_id,
                'user_id': user_id,
                'provider': provider,
                'tool_category': tool_category,
                'encrypted_credentials': credentials
            }
            tool.insert(insert_data)
        else:
            # If authorized, update existing credentials.
            conditions = [{'column': 'user_id', 'value': user_id}, {'column': 'team_id', 'value': team_id}, {'column': 'tool_category', 'value': tool_category}]
            data = {'encrypted_credentials': credentials}
            tool.update(conditions, data)
        return response_success()
        # else:
        #     # Return error if credentials are invalid.
        #     return response_error('Invalid credentials')
    except Exception as e:
        # Return error if an exception occurs.
        return response_error(str(e))


# Endpoint to delete authorization for a specific tool provider.
@router.delete("/tools_delete_authorization/{provider}")
async def skill_delete(provider: str, userinfo: TokenData = Depends(get_current_user)):
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        tool = ToolAuthorizations()
        # Define conditions for deleting tool authorization.
        conditions = [{'column': 'user_id', 'value': user_id}, {'column': 'team_id', 'value': team_id}]
        tool.delete(conditions)
        return response_success()
    except Exception as e:
        # Return error if an exception occurs.
        return response_error(str(e))
