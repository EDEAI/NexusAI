from fastapi import APIRouter
from api.utils.common import response_success, response_error
import os

router = APIRouter()

@router.get("/app_icon", response_model=dict)
async def get_app_icon():
    # Define the directory where app icons are stored
    icon_directory = "assets/app_icon"
    icon_list = []

    # Iterate over files in the icon directory
    for filename in os.listdir(icon_directory):
        # Append each file path to the icon list
        icon_list.append(f"/app_icon/{filename}")

    # Return a successful response with the list of app icons
    return response_success({
        "app_icon": icon_list
    })