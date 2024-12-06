from fastapi import APIRouter, Body, Depends
from api.schema.tools import *
from api.utils.common import *
from api.utils.jwt import *
from core.tool.provider.builtin_tool_provider import *
from core.database.models.tool_authorizations import ToolAuthorizations
from core.tool.provider.builtin_tool_provider import validate_credentials, BuiltinTool

router = APIRouter()


# Endpoint to retrieve the list of tools with their authorization status.
@router.get("/tools", response_model=toolsResponse)
async def skill_create(userinfo: TokenData = Depends(get_current_user)):
    # Fetch the available tool providers and their associated tools.
    tools = get_tool_providers_with_tools()

    for key, value in tools.items():
        # Check if the tool provider requires credentials.
        if 'credentials_for_provider' in value:
            tool = ToolAuthorizations()
            # Get the authorization status of the tool for the current user and team.
            tool_result = tool.get_tool_info(user_id=userinfo.uid, team_id=userinfo.team_id, provider=key)
            # Set authorization status based on the result.
            if tool_result["status"] != 1:
                value['authorization_status'] = 2  # Unauthorized
            else:
                value['authorization_status'] = 1  # Authorized
        else:
            # No authorization required for this tool provider.
            value['authorization_status'] = 3
    return response_success(tools)


# Endpoint to update the credentials for a specific tool provider.
@router.put("/tools_authorization/{provider}")
async def skill_update(provider: str, credentials: Dict[str, Any] = Body(...),
                       userinfo: TokenData = Depends(get_current_user)):
    user_id = userinfo.uid
    team_id = userinfo.team_id
    try:
        # Validate the provided credentials for the given provider.
        if validate_credentials(provider, credentials):
            tool = ToolAuthorizations()
            # Retrieve current authorization status for the tool.
            tool_result = tool.get_tool_info(user_id=user_id, team_id=team_id, provider=provider)
            # If the tool is not authorized, insert new credentials.
            if tool_result["status"] != 1:
                insert_data = {
                    'team_id': team_id,
                    'user_id': user_id,
                    'provider': provider,
                    'encrypted_credentials': credentials
                }
                tool.insert(insert_data)
            else:
                # If authorized, update existing credentials.
                conditions = [{'column': 'user_id', 'value': user_id}, {'column': 'team_id', 'value': team_id}]
                data = {'encrypted_credentials': credentials}
                tool.update(conditions, data)
            return response_success()
        else:
            # Return error if credentials are invalid.
            return response_error('Invalid credentials')
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
