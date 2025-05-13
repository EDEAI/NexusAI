import time
from datetime import timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from config import *
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from core.database import redis


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/login")

SECRET_KEY = settings.ACCESS_TOKEN_SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = "HS256"

class TokenData(BaseModel):
    uid: Optional[int] = None
    team_id: Optional[int] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    inviter_id: Optional[int] = None
    role: Optional[int] = None

def create_access_token(data: dict):
    """
    Create an access token.
    """
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    if expires_delta:
        expire = time.time() + expires_delta.total_seconds()
    else:
        expire = time.time() + ACCESS_TOKEN_EXPIRE_MINUTES * 60
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, credentials_exception):
    """
    Verify the token.
    """
    if redis.sismember('blacklisted_tokens', token):
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: int = payload.get("uid")
        team_id: int = payload.get("team_id")
        nickname: str = payload.get("nickname")
        phone: str = payload.get("phone")
        email: str = payload.get("email")
        inviter_id: str = payload.get("inviter_id")
        role: str = payload.get("role")
        if uid is None:
            print(f"Problem with uid: {uid}")
            raise credentials_exception
        # Get stored token from Redis
        redis_key = f"access_token:{uid}"
        stored_token = redis.get(redis_key)
        
        # Verify if token matches
        if not stored_token or stored_token.decode('utf-8') != token:
            print(f"Token mismatch for user {uid}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(uid=uid,team_id=team_id,nickname=nickname,phone=phone,email=email,inviter_id=inviter_id,role=role)
        from api.utils.auth import set_current_user_id
        set_current_user_id(uid)
    except JWTError:
        raise credentials_exception
    return token_data

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

async def get_ws_current_user(token: str):
    """
    Get the current user for websocket.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)

def blacklist_token(token: str):
    """
    Blacklist the token.
    """
    redis.sadd('blacklisted_tokens', token)
    
async def get_ws_current_user(token: str):
    """
    Get the current user for websocket.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token(token, credentials_exception)