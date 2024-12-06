from fastapi import APIRouter
from api.schema.tools import *
from api.utils.common import *
from api.utils.jwt import *
from core.database.models.models import Models

# Create a new APIRouter instance
router = APIRouter()

@router.get("/llm_model_list", response_model=toolsResponse)
async def skill_create(userinfo: TokenData = Depends(get_current_user)):
    """
    Endpoint to retrieve the list of LLM model configurations.
    
    Parameters:
    - userinfo: TokenData, required for user authentication and authorization.
    
    Returns:
    - A successful response containing the list of LLM model configurations.
    """
    # Retrieve the list of LLM model configurations from the database
    result = Models().get_model_config_llm_list()
    
    # Return the result wrapped in a success response
    return response_success({'data': result})