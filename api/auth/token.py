# Import necessary modules from FastAPI
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# Import necessary modules from the project
from api.schema.user import *
from api.utils.jwt import *
from api.utils.common import *
import hashlib  # Import hashlib for password hashing
from core.database.models.users import Users  # Import the Users model from the database


router = APIRouter()  # Create a new APIRouter instance

def fake_hash_password(password: str, timestamp: str = None):
    """
    Hash the password with an optional timestamp (salt).
    """
    password_salt = str(timestamp)  # Convert timestamp to string
    password_with_salt = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + password_salt).encode()).hexdigest()  # Hash the password with salt
    return password_with_salt

def authenticate_user(username: str, password: str):
    """
    Authenticate the user by username and password.
    """
    user_model = Users()  # Create an instance of the Users model
    user = user_model.select_one(  # Query the user from the database
        columns='*', conditions=[{'column': 'phone', 'value': username, 'logic': 'or'},{'column': 'email', 'value': username}],limit=1
    )
    if not user:  # If user not found, return False
        return False
    if not fake_hash_password(password, user["password_salt"]) == user["password"]:  # Check if the hashed password matches
        return False
    return user  # Return the authenticated user

# Endpoint to login and get access token
@router.post("/access_token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)  # Authenticate the user
    if not user:  # If authentication fails, raise HTTP 401 error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(  # Create access token for the authenticated user
        data={"uid": user["id"],"team_id": user["team_id"],"nickname": user["nickname"],"phone": user["phone"],"email": user["email"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}  # Return the access token

# Endpoint to logout the user
@router.post("/logout", response_model=ResUserLogoutSchema)
async def logout(current_user: TokenData = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    blacklist_token(token)  # Blacklist the token
    return response_success("Successfully logged out")  # Return success response

# Endpoint to get user information
@router.get("/user_info", response_model=ResUserInfoSchema)
async def get_user_info(userinfo: TokenData = Depends(get_current_user)):
    return response_success(userinfo)  # Return user information
