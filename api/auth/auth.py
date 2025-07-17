import json
from datetime import datetime
import sys, hashlib
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter,Request
from core.database.models import (
    Users,
    Teams,
    UserTeamRelations
)
from api.utils.auth import  is_valid_username, is_valid_email,authenticate_user,updata_login_ip,authenticate_third_party_user
from api.utils.common import *
from languages import get_language_content, language_packs
from api.schema.user import *
from api.utils.jwt import *
from core.database import redis,SQLDatabase
from api.utils.auth import get_uid_user_info,update_uid_language,set_current_language,set_current_user_id
from dateutil.relativedelta import relativedelta

# create router object
router = APIRouter()

@router.post('/login', response_model=Token)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_200_OK,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    team_type = Teams().select_one(
        columns=["type"],
        conditions=[
            {"column": "id", "value": user['team_id']},
            {"column": "status", "value": 1}
        ]
    )
    if team_type !=1:
        user['team_id'] = UserTeamRelations().select_one(
            columns=["team_id"],
            conditions=[
                {"column": "user_id", "value": user['id']},
                {"column": "team_id", "value": user['team_id'], "op": "!="}
            ]
        )["team_id"]
        user_update_data = {
            "team_id":user['team_id']
        }
        Users().update(
            [{'column': 'id', 'value': user['id']}],
            user_update_data
        )
    # Check if a valid token already exists in Redis
    redis_key = f"access_token:{user['id']}"
    existing_token = redis.get(redis_key)
    
    if existing_token:
        access_token = existing_token.decode('utf-8')
    else:
        access_token = create_access_token(
            data={"uid": user["id"], "team_id": user["team_id"], "nickname": user["nickname"], "phone": user["phone"],
                  "email": user["email"],"inviter_id": user["inviter_id"],"role": user["role"]}
        )
        # Store token in Redis
        redis_expiry_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60  # expiration time (using token expiration time)
        redis.set(redis_key, access_token, ex=redis_expiry_seconds)
    
    # get user language setting
    user_language = user.get("language", "zh")  # get user language
    set_current_user_id(user["id"])
    set_current_language(user["id"],user_language)  # set current language

    client_ip = request.client.host
    if client_ip:
        updata_login_ip(form_data.username, client_ip)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post('/register_team', response_model=ResRegisterTeamSchema)
async def register_team(name: str,config: str = ''):
    """
    Registers a new team with the provided name and optional configuration.
    
    Args:
        name (str): The name of the new team.
        config (str, optional): The configuration for the new team, in JSON format.
    
    Returns:
        dict: A response dictionary indicating the success or failure of the operation.
            If successful, the dictionary will contain the new team ID.
            If unsuccessful, the dictionary will contain an error message.
    """
    if name is None:
        return response_error(get_language_content('register_team_name_empty'))
    if not is_valid_username(name):
        return response_error(get_language_content('register_team_name_empty'))
    if config != '':
        config = json.dumps(config)

    team_num = Teams().select(columns='*',conditions=[{'column': 'name', 'value': name}])
    if len(team_num) > 0:
        return response_error(get_language_content('register_team_name_repeat'))

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    team_id = Teams().insert({'name': name,'config':config,'created_time': formatted_time})
    if team_id > 0:
        return response_success({"team_id": team_id})
    return response_error(get_language_content('register_team_failed'))

@router.post('/register_user', response_model=ResDictSchema)
async def register_user(register_user: RegisterUserData):
    email = register_user.email
    password = register_user.password
    nickname = register_user.nickname
    if not nickname:
        return response_error(get_language_content('register_nickname_empty'))
    if len(nickname.encode('utf-8')) > 50:
        return response_error(get_language_content('register_nickname_long'))
    if not email:
        return response_error(get_language_content('register_email_failed'))
    if not is_valid_email(email):
        return response_error(get_language_content('register_email_illegality'))
    if not password:
        return response_error(get_language_content('register_password_failed'))

    # if not is_valid_phone_number(phone):
    #     return response_error(get_language_content('register_phone_illegality'))
    # if phone == '':
    #     return response_error(get_language_content('register_phone_failed'))
    # if get_repeat_phone(phone):
    #     return response_error(get_language_content('register_phone_repeat'))

    user_data = Users().select_one(columns='*', conditions=[{'column': 'email', 'value': email, 'logic':'or'},{'column': 'phone', 'value': email}])

    if not user_data:
        return response_error(get_language_content('register_email_empty'))
    elif user_data and user_data['password'] != 'nexus_ai123456':
        return response_error(get_language_content('register_email_repeat'))

    password_salt = str(int(datetime.now().timestamp()))
    password_with_salt = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + password_salt).encode()).hexdigest()

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    register_user_data = {
        'nickname': nickname,
        'email': email,
        'password': password_with_salt,
        'password_salt': password_salt,
        'created_time': formatted_time,
    }

    user_id = Users().update(
        [{'column': 'id', 'value': user_data['id']}],
        register_user_data
    )
    SQLDatabase.commit()
    SQLDatabase.close()
    if not user_id:
        return response_error(get_language_content('register_password_failed'))
    user_info = Users().select_one(columns='*', conditions=[{'column': 'id', 'value': user_data['id']}])
    return response_success({"user_info": user_info})

@router.post("/logout", response_model=ResUserLogoutSchema)
async def logout(current_user: TokenData = Depends(get_current_user), token: str = Depends(oauth2_scheme)):
    """
    Logs out the current user by deleting their access token from Redis.
    
    Args:
        current_user (TokenData): The current user's token data, obtained using the `get_current_user` dependency.
        token (str): The token to be deleted, obtained using the `oauth2_scheme` dependency.
    
    Returns:
        A success response with the message "Successfully logged out".
    """
        
    # Delete the token directly from Redis based on user type
    if current_user.user_type == "third_party":
        redis_key = f"third_party_access_token:{current_user.uid}"
    else:
        redis_key = f"access_token:{current_user.uid}"
    redis.delete(redis_key)
    
    return response_success("Successfully logged out")

@router.get("/user_info", response_model=ResUserInfoSchema)
async def get_user_info(userinfo: TokenData = Depends(get_current_user)):
    """
    Returns the user information for the current authenticated user.
    
    Args:
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.
    
    Returns:
        A success response containing the user information.
    """
    uid = userinfo.uid
    
    # Get user info (works for both regular and third-party users)
    user_info = get_uid_user_info(uid)
    if user_info:
        user_info['uid'] = uid
        # Set user type based on whether platform and openid exist
        if user_info.get('platform') and user_info.get('openid'):
            user_info['user_type'] = 'third_party'
        else:
            user_info['user_type'] = 'regular'
    else:
        return response_error("User not found")
    
    return response_success(user_info)

@router.post("/switch_the_language", response_model=ResDictSchema)
async def switch_the_language(data:SwitchLanguageSchema,userinfo: TokenData = Depends(get_current_user)):
    """
    Switch the language for the current user.
    
    Args:
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.
    
    Returns:
        A success response indicating the language has been switched.
    """
    language = data.language
    if language not in language_packs:
        return response_error(get_language_content('switch_the_language_failed'))
    user_language_update = update_uid_language(userinfo.uid,language)
    if not user_language_update:
        return response_error(get_language_content('switch_the_language_failed'))
    set_current_language(userinfo.uid,language)
    return response_success(detail = get_language_content('switch_the_language_success'))


@router.post("/invite_user", response_model=ResDictSchema)
async def invite_user(invite_data: CreateDataEmailList,request:Request, userinfo: TokenData = Depends(get_current_user)):
    """
    Return the invitation link for the currently verified user.

    Args：
        Userinfo (TokenData): The token data of the currently verified user is obtained using the 'get_current_user' dependency relationship.

    Returns:
        Successfully returned the user invitation link accordingly.
    """
    email_list_res = []
    url_list = []

    role_id = invite_data.role
    email_list = invite_data.email_list

    if not email_list:
        return response_error(get_language_content('lnvitation_email_failed'))
    
    team = Teams().select_one(columns=['name'], conditions=[{'column': 'id', 'value': userinfo.team_id}, {'column': 'status', 'value': 1}])
    if not team:
        return response_error(get_language_content('lnvitation_team_failed'))
    
    # Check if there are any existing users in the invitation list
    user_info = Users().select(columns='*', conditions=[{'column': 'email', 'op' : 'in', 'value': email_list}])
    if user_info:
        for value in user_info:
            if value['password'] == 'nexus_ai123456':
                url_list.append(
                    settings.WEB_URL + '/user/register?email=' + value['email'] + '&team=' + team['name']
                )
            else:
                url_list.append(
                    settings.WEB_URL + '/user/login?email=' + value['email']
                )
            UserTeamRelations().ensure_team_id_exists(userinfo.team_id, value['email'])
            email_list_res.append(value['email'])
    # Remove identical elements from two lists
    common_elements = set(email_list_res) & set(email_list)
    email_list = list(filter(lambda x: x not in common_elements, email_list))
    # Organize data
    for val in email_list:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        user_data = {
                'team_id': userinfo.team_id,
                'inviter_id': userinfo.uid,
                'nickname': '',
                'role': role_id,
                'phone': '',
                'email': val,
                'password': 'nexus_ai123456',
                'password_salt': '123456',
                'created_time': formatted_time,
            }
        user_id = Users().insert(user_data)
        if not user_id:
            return response_error(get_language_content('lnvitation_failed'))
        UserTeamRelations().ensure_team_id_exists(userinfo.team_id, val)
        url_list.append(
            settings.WEB_URL + '/user/register?email=' + val + '&team=' + team['name']
        )
        SQLDatabase.commit()
        SQLDatabase.close()
    return response_success({'email_list': url_list})

@router.get("/team_member_list", response_model=ResDictSchema)
async def invite_user(team_id: int = 1,userinfo: TokenData = Depends(get_current_user)):
    """
      team_id: int, team id.(Reserved fields may not be transmitted)
    """
    team_member_list = []
    # user_info_list = Users().select(columns='*', conditions=[{'column': 'team_id', 'value': team_id},{'column': 'status', 'value': 1}])
    user_info_list = UserTeamRelations().select(
        columns=[
            'users.email',
            'users.last_login_time',
            'users.id',
            'users.avatar',
            'users.nickname',
            'users.role'
        ],
        conditions=[{'column': 'user_team_relations.team_id', 'value': team_id}],
        joins=[
            ["left", "users", "user_team_relations.user_id = users.id"]
        ]
    )

    team_data = Teams().select_one(columns='*', conditions=[{'column': 'id', 'value': team_id}])
    team_name = 'No team currently available'
    if team_data:
        team_name = team_data['name']
    if user_info_list:
        now = datetime.now()
        for index, value in enumerate(user_info_list):
            if value['email']:
                if value['last_login_time']:
                    delta = now - value['last_login_time']
                    rel_delta = relativedelta(now, value['last_login_time'])

                    minutes = delta.total_seconds() / 60
                    hours = minutes / 60
                    days = delta.days
                    months = rel_delta.months + rel_delta.years * 12
                    years = rel_delta.years

                    if years >= 1:
                        time_text = f"{years}{get_language_content('login_time_last_year')}"
                    elif months >= 1:
                        time_text = f"{months}{get_language_content('login_time_a_month_ago')}"
                    elif days >= 1:
                        time_text = f"{days}{get_language_content('login_time_days_ago')}"
                    elif hours >= 1:
                        time_text = f"{hours:.0f}{get_language_content('login_time_hours_ago')}"
                    elif minutes >= 1:
                        time_text = f"{minutes:.0f}{get_language_content('login_time_minutes_ago')}"
                    else:
                        time_text = {get_language_content('login_time_just')}
                else:
                    time_text = {get_language_content('login_time_never_logged_in')}

                member_info = {
                    'user_id': value['id'],
                    'avatar': value['avatar'],
                    'nickname': value['nickname'],
                    'email': value['email'],
                    'role': value['role'],
                    'last_login_time': time_text
                }
                team_member_list.append(member_info)
    SQLDatabase.commit()
    SQLDatabase.close()
    return response_success({'team_name':team_name, 'team_member_list':team_member_list})

@router.get('/user_teams', response_model=ResDictSchema)
async def get_user_teams(platform: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Returns all teams for the current authenticated user by user_id, joined with the teams table.

    Args:
        platform (int): 1 for web, 2 for third-party.
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.

    Returns:
        A success response containing the list of teams the user belongs to.
    """
    user_id = userinfo.uid
    # Get the id of the team with type=2 (personal workspace)
    personal_team = Teams().select_one(columns=["id"], conditions=[{"column": "type", "value": 2}])
    personal_team_id = personal_team["id"] if personal_team else None
    conditions = [
        {'column': 'user_team_relations.user_id', 'value': user_id}
    ]
    if platform == 1 and personal_team_id:
        conditions.append({'column': 'user_team_relations.team_id', 'value': personal_team_id, 'op': '!='})
    user_teams = UserTeamRelations().select(
        columns=[
            'teams.id',
            'teams.name',
            'teams.config',
            'teams.created_time',
            'teams.updated_time',
            'teams.status',
            'teams.type'
        ],
        conditions=conditions,
        joins=[
            ["left", "teams", "user_team_relations.team_id = teams.id"]
        ]
    )
    return response_success({'teams': user_teams})

@router.post('/switch_team', response_model=ResDictSchema)
async def switch_user_team(team_id: int, userinfo: TokenData = Depends(get_current_user)):
    """
    Switches the current user's team_id and saves it.

    Args:
        team_id (int): The ID of the team to switch to.
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.

    Returns:
        A success response with the new team_id if the switch is successful, otherwise an error response.
    """
    user_id = userinfo.uid
    # Check if the user belongs to the specified team
    relation = UserTeamRelations().select_one(
        columns=["id"],
        conditions=[
            {"column": "user_id", "value": user_id},
            {"column": "team_id", "value": team_id}
        ]
    )
    if not relation:
        return response_error(get_language_content('user_does_not_belong_to_this_team'))
    Users().update(
        [{"column": "id", "value": user_id}],
        {"team_id": team_id}
    )
    return response_success({"team_id": team_id})

@router.post('/third_party_login', response_model=ResThirdPartyLoginSchema)
async def third_party_login(request: Request, login_data: ThirdPartyLoginData):
    """
    Third-party user login/register endpoint.
    
    This endpoint handles both login and registration for third-party users.
    If the user exists, it will log them in and return a token.
    If the user doesn't exist, it will register them first, then log them in.
    
    Args:
        request (Request): The request object to get client IP.
        login_data (ThirdPartyLoginData): The third-party login data containing:
            - platform: Third-party platform identifier
            - openid: User's openid on the platform
            - nickname: User's nickname (optional)
            - avatar: User's avatar URL (optional)
            - language: User's language preference (optional, defaults to 'en')
    
    Returns:
        ResThirdPartyLoginSchema: Response containing access token and user info.
    """
    # Get client IP
    client_ip = request.client.host
    if request.headers.get("X-Forwarded-For"):
        client_ip = request.headers.get("X-Forwarded-For").split(",")[0]
    elif request.headers.get("X-Real-IP"):
        client_ip = request.headers.get("X-Real-IP")
    
    # Validate required parameters
    if not login_data.platform or not login_data.openid:
        return response_error(get_language_content('login_user_name_empty'))
    
    # Authenticate or register third-party user
    user = authenticate_third_party_user(
        platform=login_data.platform,
        openid=login_data.openid,
        nickname=login_data.nickname,
        avatar=login_data.avatar,
        language=login_data.language or 'en',
        client_ip=client_ip,
        phone=login_data.phone,
        email=login_data.email
    )
    
    if not user:
        return response_error(get_language_content('login_user_password_failed'))
    
    # Check if a valid token already exists in Redis
    redis_key = f"third_party_access_token:{user['id']}"
    existing_token = redis.get(redis_key)
    
    if existing_token:
        access_token = existing_token.decode('utf-8')
    else:
        # Create access token for third-party user
        access_token = create_access_token(
            data={
                "uid": user["id"], 
                "team_id": user["team_id"],
                "nickname": user["nickname"],
                "phone": user["phone"],
                "email": user["email"],
                "inviter_id": user["inviter_id"],
                "role": user["role"],
                "platform": user["platform"],
                "openid": user["openid"],
                "language": user["language"],
                "user_type": "third_party"  # Add user type to distinguish from regular users
            }
        )
        # Store token in Redis
        redis_expiry_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
        redis.set(redis_key, access_token, ex=redis_expiry_seconds)
    
    # Get user language setting
    user_language = user.get("language", "en")
    set_current_user_id(user["id"])
    set_current_language(user["id"], user_language)
    
    # Prepare response data
    response_data = {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "uid": user["id"],
            "nickname": user["nickname"],
            "avatar": user["avatar"],
            "language": user["language"],
            "platform": user["platform"],
            "openid": user["openid"]
        }
    }
    
    return response_success(response_data)