import json
import re
from base64 import b64decode
from hashlib import md5
from traceback import format_exc
from typing import Any, Callable, Coroutine, Dict, Union
from Crypto.Cipher import AES
from fastapi import HTTPException, Request, APIRouter, Depends, status
from core.database import redis, SQLDatabase
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from api.schema.user import *
from api.utils.jwt import *
from api.utils.common import *
import hashlib
from core.database.models.users import Users
from contextvars import ContextVar
from languages import language_packs

router = APIRouter()


def aes_decrypt(func: Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]):
    """
    Decorator function for AES decryption.
    
    This function decrypts the 'data' field from the request form using AES encryption.
    It uses a fixed key derived from 'NEXUSAI' for decryption.
    
    Args:
        func (Callable): The function to be decorated.
    """
    async def decorator(request: Request):
        form = await request.form()
        data = form['data']
        m = md5(b'NEXUSAI')
        key = m.hexdigest().encode()
        aes = AES.new(key, AES.MODE_ECB)
        decrypted_data = aes.decrypt(b64decode(data)).rstrip(b'\0')
        decrypted_data = json.loads(decrypted_data)
        if 'file' in form:
            decrypted_data['file'] = form['file']
        try:
            return await func(decrypted_data)
        except:
            return HTTPException(500, format_exc())
    return decorator

def aes_decrypt_with_token(func: Callable[[Dict[str, Any]], Coroutine[Any, Any, Any]]):
    """
    Decorator function for AES decryption with token-based authentication.
    
    This function decrypts the 'data' field from the request form using AES encryption.
    It uses a token stored in Redis for the given user_id as the encryption key.
    
    Args:
        func (Callable): The function to be decorated.
    """
    async def decorator(request: Request):
        form = await request.form()
        user_id = form['user_id']
        data = form['data']
        key = redis.get(f'TOKEN_{user_id}')
        if key is None:
            return HTTPException(401, 'Please login to continue')
        m = md5(key)
        key = m.hexdigest().encode()
        aes = AES.new(key, AES.MODE_ECB)
        decrypted_data = aes.decrypt(b64decode(data)).rstrip(b'\0')
        decrypted_data = json.loads(decrypted_data)
        decrypted_data['user_id'] = user_id
        if 'file' in form:
            decrypted_data['file'] = form['file']
        try:
            return await func(decrypted_data)
        except:
            return HTTPException(500, format_exc())
    return decorator

def is_valid_username(check_name: str) -> str:
    """
    Check if the name is valid:
    1. The byte length ranges from 4 to 50 bytes;
    2. It can only contain letters, numbers, underscores, spaces, and Chinese characters;
    4. Continuous underscores or spaces are not allowed in the title.
    """
    title_length = len(check_name.encode('utf-8'))
    if not 4 <= title_length <= 50:
        return False
    pattern = r'^[A-Za-z_\u4e00-\u9fa5][A-Za-z0-9_\u4e00-\u9fa5 ]*$'
    if not re.match(pattern, check_name):
        return False
    if re.search(r'__|  ', check_name):
        return False
    return True

def is_valid_phone_number(check_phone: str) -> str:
    """
    Check if the phone number is valid:
    1. The length is 11 digits;
    2. Start with 13, 14, 15, 16, 17, 18, 19.
    """
    pattern = r'^(13[0-9]|14[0-9]|15[0-9]|16[0-9]|17[0-9]|18[0-9]|19[0-9])\d{8}$'
    if re.match(pattern, check_phone):
        return True
    return False

def is_valid_email(check_email: str) -> str:
    """

    Check if the email is valid:

    1. Contains a '@' symbol;

    The part before '@' can contain letters, numbers, underscores, dots, and minus signs;

    The part after '@' must contain a dot '.', And it can contain letters, numbers, and minus signs, and the dots cannot appear consecutively.

    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, check_email) is not None

def fake_hash_password(password: str, timestamp: str = None):
    """
    Hash the password with a timestamp.
    """
    password_salt = str(timestamp)
    password_with_salt = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + password_salt).encode()).hexdigest()
    return password_with_salt

def authenticate_user(username: str, password: str):
    """
    Authenticate the user.
    """
    user_model = Users()
    user = user_model.select_one(
        columns='*', conditions=[{'column': 'phone', 'value': username, 'logic': 'or'},{'column': 'email', 'value': username}]
    )
    if not user:
        return False
    if not fake_hash_password(password, user["password_salt"]) == user["password"]:
        return False
    return user

def get_repeat_email(email: str):
    """
    Check if the email is already registered.
    """
    user_model = Users()
    user = user_model.select_one(
        columns='*', conditions=[{'column': 'email', 'value': email}]
    )
    if not user:
        return False
    return True

def get_repeat_phone(phone: str):
    """
    Check if the phone number is already registered.
    """
    user_model = Users()
    user = user_model.select_one(
        columns='*', conditions=[{'column': 'phone', 'value': phone}]
    )
    if not user:
        return False
    return True

def updata_login_ip(username: str, client_ip: str):
    """
    Update the login IP and time for the user.
    """
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    user_model = Users()
    user_id = user_model.update(
        [{'column': 'phone', 'value': username, 'logic': 'or'},{'column': 'email', 'value': username}],{'last_login_ip': client_ip,'last_login_time': formatted_time}
    )
    SQLDatabase.commit()
    SQLDatabase.close()

    if not user_id:
        return False
    return True
def get_uid_user_info(uid:int):
    '''
    Retrieve user information by user ID.
    '''
    user_model = Users()
    user = user_model.select_one(
        columns='*', conditions=[{'column': 'id', 'value': uid}]
    )
    if not user:
        return False
    
    return user

def update_uid_language(uid:int,language:str):
    '''
    Update the language for the user by user ID.
    '''
    user_model = Users()
    user = user_model.update(
        [{'column': 'id', 'value': uid}],{'language': language}
    )
    SQLDatabase.commit()
    SQLDatabase.close()
    if not user:
        return False
    return True

current_user_id = ContextVar('current_user_id', default=None)

def set_current_user_id(uid: int):
    current_user_id.set(uid)

def get_current_user_id() -> int:
    return current_user_id.get()

def set_current_language(user_id: int, language: str):
    redis.set("user_language:{}".format(user_id), language if language in language_packs else 'en')

def get_current_language(uid:int = 0) -> str:
    if uid > 0:
        user_id = uid
    else:
        user_id = get_current_user_id()
        if user_id is None:
            return 'en'
    language_data = redis.get("user_language:{}".format(user_id))
    if language_data:
        return language_data.decode('utf-8')
    else:
        user_language = Users().get_user_language(user_id)
        redis.set("user_language:{}".format(user_id), user_language if user_language in language_packs else 'en')
        return user_language

def authenticate_third_party_user(platform: str, openid: str, sundry: Union[str, int, None] = None, nickname: str = None, 
                                  avatar: str = None, language: str = 'en', 
                                  client_ip: str = None, phone: str = None, email: str = None):
    """
    Authenticate or register a third-party user.
    
    :param platform: The third-party platform identifier.
    :param openid: The user's openid on the platform.
    :param nickname: The user's nickname (optional).
    :param avatar: The user's avatar URL (optional).
    :param language: The user's language preference.
    :param client_ip: The user's login IP.
    :return: The user data if successful, False otherwise.
    """
    try:
        user_model = Users()
        
        # Create or update user and get user ID
        user_id = user_model.create_or_update_third_party_user(
            platform=platform,
            openid=openid,
            sundry=sundry,
            nickname=nickname,
            avatar=avatar,
            language=language,
            last_login_ip=client_ip,
            phone=phone,
            email=email
        )
        # Commit the transaction
        SQLDatabase.commit()
        SQLDatabase.close()
        
        # Get the complete user data
        user = user_model.select_one(
            columns='*',
            conditions=[
                {'column': 'id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ]
        )
        user['openid'] = openid
        user['platform'] = platform
        if user:
            return user
        else:
            return False
    except Exception as e:
        SQLDatabase.rollback()
        SQLDatabase.close()
        print(f"Error in authenticate_third_party_user: {e}")
        return False

def get_third_party_user_info(uid: int):
    """
    Retrieve third-party user information by user ID.
    
    :param uid: The user ID.
    :return: The user data if found, False otherwise.
    """
    user_model = Users()
    user = user_model.select_one(
        columns='*',
        conditions=[
            {'column': 'id', 'value': uid},
            {'column': 'status', 'value': 1}
        ]
    )
    if not user:
        return False
    return user

def authenticate_third_party_user_binding(platform: str, openid: str, sundry: Union[str, int, None] = None, nickname: str = None, 
                                  avatar: str = None, language: str = 'en', 
                                  client_ip: str = None, phone: str = None, email: str = None):
    """
    Authenticate or register a third-party user.
    
    :param platform: The third-party platform identifier.
    :param openid: The user's openid on the platform.
    :param nickname: The user's nickname (optional).
    :param avatar: The user's avatar URL (optional).
    :param language: The user's language preference.
    :param client_ip: The user's login IP.
    :return: The user data if successful, False otherwise.
    """
    try:
        user_model = Users()
        
        # Create or update user and get user ID
        user_id = user_model.create_or_update_third_party_user_binding(
            platform=platform,
            openid=openid,
            sundry=sundry,
            nickname=nickname,
            avatar=avatar,
            language=language,
            last_login_ip=client_ip,
            phone=phone,
            email=email
        )
        # Commit the transaction
        SQLDatabase.commit()
        SQLDatabase.close()
        # Get the complete user data
        user = user_model.select_one(
            columns='*',
            conditions=[
                {'column': 'id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ]
        )
        user['openid'] = openid
        user['platform'] = platform
        if user:
            return user
        else:
            return False
    except Exception as e:
        SQLDatabase.rollback()
        SQLDatabase.close()
        print(f"Error in authenticate_third_party_user: {e}")
        return False

