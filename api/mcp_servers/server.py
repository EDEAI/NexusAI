from fastapi import APIRouter
from typing import Optional
from core.database.models.mcp_server import McpServer
from api.schema.mcp_servers import *
from api.utils.common import *
from api.utils.jwt import *
import json
import sys, os
from time import time
from datetime import datetime
from languages import get_language_content
router = APIRouter()

@router.get("/", response_model=McpServerListResponse, summary="Get MCP Server List")
async def servers_list(page: int = 1, page_size: int = 10, name: str = "", userinfo: TokenData = Depends(get_current_user)):
    """
    Retrieve a list of MCP servers.
    
    This endpoint retrieves all available MCP servers with pagination and name filtering support.
    
    Parameters:
    - page (int): Current page number, defaults to 1
    - page_size (int): Number of items per page, defaults to 10
    - name (str): Optional server name for fuzzy search
    - userinfo (TokenData): Current user information, obtained through authentication
    
    Returns:
    - Standard response containing server list, formatted according to McpServerListResponse model
    
    Raises:
    - HTTPException: When query execution fails
    """
    mcp_server = McpServer()
    result = mcp_server.get_server_list(page, page_size, name)
    return response_success(result)