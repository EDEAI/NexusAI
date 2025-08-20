import json
from datetime import datetime
import sys, hashlib
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter,Request
from core.database.models import (
    Users,
    Teams,
    UserTeamRelations,
    UserThreeParties,
    Roles
)
from api.utils.auth import  is_valid_username, is_valid_email,authenticate_user,updata_login_ip,authenticate_third_party_user,authenticate_third_party_user_binding
from api.utils.common import *
from languages import get_language_content, language_packs
from api.schema.user import *
from api.utils.jwt import *
from core.database import redis,SQLDatabase
from api.utils.auth import get_uid_user_info,update_uid_language,set_current_language,set_current_user_id
from dateutil.relativedelta import relativedelta

from config import settings
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
    if team_type['type'] !=1:
        user_info = UserTeamRelations().select_one(
            columns="*",
            conditions=[
                {"column": "user_id", "value": user['id']},
                {"column": "team_id", "value": user['team_id'], "op": "!="}
            ]
        )
        user_update_data = {
            "team_id":user_info['team_id'], 
            "role":user_info['role'], 
            "inviter_id":user_info['inviter_id'], 
            "role_id":user_info['role_id']
        }
        Users().update(
            [{'column': 'id', 'value': user['id']}],
            user_update_data
        )
        user['team_id'] = user_info['team_id']
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
    position = register_user.position
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

    conditions = [
        {"column": "status", "value": 1},
        [
            {"column": "email", "value": email, "op": "=", "logic": "or"},
            {"column": "phone", "value": email, "op": "="}
        ]
    ]

    user_data = Users().select_one(
        columns='*', 
        conditions = conditions
    )

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
        # 'position': position,
        'email': email,
        'password': password_with_salt,
        'password_salt': password_salt,
        'created_time': formatted_time,
    }

    user_id = Users().update(
        [{'column': 'id', 'value': user_data['id']}],
        register_user_data
    )

    if position is not None and position != '' and position.strip() != '':
        team_id = user_data['team_id']
        user_id = user_data['id']
        UserTeamRelations().update_user_position(user_id, team_id, position)
    SQLDatabase.commit()
    SQLDatabase.close()
    if not user_id:
        return response_error(get_language_content('register_password_failed'))
    user_info = Users().select_one(columns='*', conditions=[{'column': 'id', 'value': user_data['id']}])
    get_user_team_relation = UserTeamRelations().get_user_team_relation(user_info['id'],user_info['team_id'])
    if get_user_team_relation:
        user_info['position'] = get_user_team_relation['position']
    else:
        user_info['position'] = ''
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
        # # Set user type based on whether platform and openid exist
        # if user_info.get('platform') and user_info.get('openid'):
        #     user_info['user_type'] = 'third_party'
        # else:
        #     user_info['user_type'] = 'regular'
        if user_info['team_id']:
            team_type = Teams().select_one(
                columns=['type'], 
                conditions=[
                    {'column': 'id', 'value': user_info['team_id']}, 
                    {'column': 'status', 'value': 1}
                ]
            )['type']
            user_info['team_type'] = team_type
        else:
            user_info['team_type'] = 1
        user_info['team_name'] =  Teams().select_one(
            columns=['name'], 
            conditions=[
                {'column': 'id', 'value': user_info['team_id']}, 
                {'column': 'status', 'value': 1}
            ]
        )['name']
        # Always include three_list regardless of team_id
        user_info['three_list'] = UserThreeParties().select(
            columns=['platform','openid','sundry'], 
            conditions=[
                {'column': 'user_id', 'value': uid}
            ]
        )

        get_user_team_relation = UserTeamRelations().get_user_team_relation(user_info['id'],user_info['team_id'])
        if get_user_team_relation:
            user_info['position'] = get_user_team_relation['position']
            user_info['role_id'] = get_user_team_relation['role_id']
            user_info['role'] = get_user_team_relation['role']
            
            # Get user's role permissions
            if get_user_team_relation['role_id']:
                from core.database.models.role_permission import RolePermission
                from core.database.models.permissions import Permission
                from core.database.models.users import Users
                
                role_perm_model = RolePermission()
                permission_model = Permission()
                
                # Get permission IDs for this role
                permission_ids = role_perm_model.get_permission_ids_by_role_id(get_user_team_relation['role_id'])
                
                user_permissions = []
                if permission_ids:
                    # Get user language preference
                    user_language = Users().get_user_language(uid)
                    
                    # Determine columns based on language
                    if user_language == 'zh':
                        permission_columns = [
                            "id",
                            "title_cn AS title",
                            "status",
                            "created_at",
                            "updated_at"
                        ]
                    else:
                        permission_columns = [
                            "id",
                            "title_en AS title",
                            "status",
                            "created_at",
                            "updated_at"
                        ]
                    
                    # Get permission details
                    user_permissions = permission_model.select(
                        columns=permission_columns,
                        conditions=[
                            {"column": "id", "op": "in", "value": permission_ids},
                            {"column": "status", "value": 1}
                        ],
                        order_by="id ASC"
                    )
                
                user_info['permissions'] = user_permissions
            else:
                user_info['permissions'] = []
        else:
            user_info['position'] = ''
            user_info['role_id'] = None
            user_info['permissions'] = []

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
    already_registered_emails = []  # Store already registered emails
    valid_emails = []  # Store valid emails that can be invited

    role_id = invite_data.role
    if role_id == 'admin_user':
        role = 1
        role_id = None
    else:
        role = 2
    email_list = invite_data.email_list
    send_email = invite_data.send_email  # 0: return links, 1: send emails

    if not email_list:
        return response_error(get_language_content('lnvitation_email_failed'))
    
    team = Teams().select_one(columns=['name'], conditions=[{'column': 'id', 'value': userinfo.team_id}, {'column': 'status', 'value': 1}])
    if not team:
        return response_error(get_language_content('lnvitation_team_failed'))
    
    # Check if there are any existing users in the invitation list
    user_info = Users().select(columns='*', conditions=[{'column': 'email', 'op' : 'in', 'value': email_list},{'column': 'status', 'value': 1}])
    
    if user_info:
        for value in user_info:
            if value['password'] == 'nexus_ai123456':
                # Unregistered user (default password), can be invited
                url_list.append(
                    settings.WEB_URL + '/user/register?email=' + value['email'] + '&team=' + team['name']
                )
                email_list_res.append(value['email'])
                valid_emails.append(value['email'])
            else:
                # Already registered user (non-default password), record as registered
                already_registered_emails.append(value['email'])
            
            UserTeamRelations().ensure_team_id_exists(userinfo.team_id, value['email'], role, role_id)
    
    # Remove identical elements from two lists (exclude processed emails)
    processed_emails = set(email_list_res) | set(already_registered_emails)
    remaining_emails = list(filter(lambda x: x not in processed_emails, email_list))
    
    # Organize data for new users
    for val in remaining_emails:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        user_data = {
                'team_id': userinfo.team_id,
                'inviter_id': userinfo.uid,
                'nickname': '',
                'role': role,
                'role_id': role_id,
                'phone': '',
                'email': val,
                'password': 'nexus_ai123456',
                'password_salt': '123456',
                'created_time': formatted_time,
            }
        user_id = Users().insert(user_data)
        if not user_id:
            return response_error(get_language_content('lnvitation_failed'))
        UserTeamRelations().ensure_team_id_exists(userinfo.team_id, val, role, role_id)
        url_list.append(
            settings.WEB_URL + '/user/register?email=' + val + '&team=' + team['name']
        )
        valid_emails.append(val)
        SQLDatabase.commit()
        SQLDatabase.close()
    
    # Build return result
    result_data = {'email_list': url_list}
    
    # Build message list
    messages = []
    
    # Email sending logic
    if send_email == 1 and valid_emails:
        from core.smtp.emails_smtp import SMTPEmailSender
        
        # Get current user info as inviter
        current_user_info = Users().select_one(
            columns=['nickname'], 
            conditions=[{'column': 'id', 'value': userinfo.uid}]
        )
        inviter_name = current_user_info.get('nickname', '') if current_user_info else ''
        
        email_sender = SMTPEmailSender()
        email_success_count = 0
        email_failed_count = 0
        
        # Send email to each valid email address
        for i, email_addr in enumerate(valid_emails):
            if i < len(url_list):
                invitation_url = url_list[i]
                try:
                    success, message = email_sender.send_user_invitation(
                        to_email=email_addr,
                        invitation_url=invitation_url,
                        team_name=team['name'],
                        inviter_name=inviter_name
                    )
                    
                    if success:
                        email_success_count += 1
                    else:
                        email_failed_count += 1
                        
                except Exception as e:
                    email_failed_count += 1
        
        # Add email sending result message
        # if email_failed_count == 0:
        messages.append(get_language_content('invitation_emails_sent_successfully'))
        # else:
            # messages.append(f"Email sending completed, {email_success_count} successful, {email_failed_count} failed")
    
    elif send_email == 0:
        # Only return links case
        if valid_emails:
            messages.append(get_language_content('invitation_links_generated_successfully'))
    
    # Add already registered emails message
    if already_registered_emails:
        message = ''
        # registered_emails_str = ', '.join(already_registered_emails)
        # if len(already_registered_emails) == 1:
        #     messages.append(get_language_content('email_already_registered').format(email=registered_emails_str))
        # else:
        #     messages.append(f"{get_language_content('some_emails_already_registered')}: {registered_emails_str}")
    
    # Set final msg
    if messages:
        result_data['msg'] = '; '.join(messages)
    else:
        result_data['msg'] = get_language_content('invitation_links_generated_successfully')
    
    return response_success(result_data)


@router.get("/team_member_list", response_model=ResDictSchema)
async def invite_user(keyword: str = None, userinfo: TokenData = Depends(get_current_user)):
    """
      team_id: int, team id.(Reserved fields may not be transmitted)
      role: When role equals 1, use the frontend language pack; when role equals 2, use user_title.
      keyword: Optional search keyword for nickname and email
    """
    team_id = userinfo.team_id
    team_member_list = []
    
    # Build conditions for the query
    conditions = [{'column': 'user_team_relations.team_id', 'value': team_id}]
    
    # Add keyword search conditions if keyword is provided
    if keyword:
        like_value = f"%{keyword}%"
        conditions.append([
            {'logic': 'or', 'column': 'users.nickname', 'op': 'like', 'value': like_value},
            {'column': 'users.email', 'op': 'like', 'value': like_value}
        ])
    
    user_info_list = UserTeamRelations().select(
        columns=[
            'users.email',
            'users.last_login_time',
            'users.id',
            'users.avatar',
            'users.nickname',
            'user_team_relations.role',
            'user_team_relations.position',
            'user_team_relations.role_id'
        ],
        conditions=conditions,
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
            if value['role'] == 1:
                user_title = 'Administrator'
            else:
                role_data = Roles().select_one(columns='*', conditions=[{'column': 'id', 'value': value['role_id']}])
                if role_data:
                    if role_data['built_in'] == 1:
                        user_title = get_language_content(role_data['name'])
                    else:
                        user_title = role_data['name']
                else:
                    user_title = 'Unknown Role'  # Default role name when role doesn't exist
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
                    'role_id': value['role_id'],
                    'position': value['position'],
                    'role_title': user_title,
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
            'teams.type',
            'user_team_relations.position',
            'user_team_relations.role',
            'user_team_relations.role_id'
        ],
        conditions=conditions,
        joins=[
            ["left", "teams", "user_team_relations.team_id = teams.id"]
        ]
    )
    
    # Process each team to add role_name and member_count
    for team in user_teams:
        # Set role name based on role value


        if team['role'] == 1:
            user_title = 'Administrator'
        else:
            role_data = Roles().select_one(columns='*', conditions=[{'column': 'id', 'value': team['role_id']}])
            if role_data:
                if role_data['built_in'] == 1:
                    user_title = get_language_content(role_data['name'])
                else:
                    user_title = role_data['name']
            else:
                user_title = 'Unknown Role'  # Default role name when role doesn't exist
        team['role_name']= user_title
        # Count total members in this team
        team_members = UserTeamRelations().select(
            columns=['id'],
            conditions=[{'column': 'team_id', 'value': team['id']}]
        )
        team['member_count'] = len(team_members) if team_members else 0
    
    return response_success({'teams': user_teams})

@router.post('/switch_team', response_model=ResDictSchema)
async def switch_user_team(team_id: SwitchTeamId, userinfo: TokenData = Depends(get_current_user)):
    """
    Switches the current user's team_id and saves it to both database and Redis cache.

    Args:
        team_id (int): The ID of the team to switch to.
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.

    Returns:
        A success response with the new team_id if the switch is successful, otherwise an error response.
    """
    team_id_value = team_id.team_id
    user_id = userinfo.uid
    # Check if the user belongs to the specified team
    relation = UserTeamRelations().select_one(
        columns='*',
        conditions=[
            {"column": "user_id", "value": user_id},
            {"column": "team_id", "value": team_id_value}
        ]
    )
    if not relation:
        return response_error(get_language_content('user_does_not_belong_to_this_team'))
    
    # Update user information to database
    Users().update(
        [{"column": "id", "value": user_id}],
        {"team_id": team_id_value, "role":relation['role'], "inviter_id":relation['inviter_id'], "role_id":relation['role_id']}
    )
    
    # Update Redis token cache with new team information
    # Determine Redis key based on user type
    if hasattr(userinfo, 'user_type') and userinfo.user_type == "third_party":
        token_redis_key = f"third_party_access_token:{user_id}"
    else:
        token_redis_key = f"access_token:{user_id}"
    
    new_access_token = None
    # Check if token exists in Redis and update it with new team information
    existing_token = redis.get(token_redis_key)
    if existing_token:
        # Get updated user information from database
        updated_user = Users().select_one(
            columns=['id', 'team_id', 'nickname', 'phone', 'email', 'inviter_id', 'role'],
            conditions=[{"column": "id", "value": user_id}]
        )
        
        if updated_user:
            # Create new token with updated team information
            token_data = {
                "uid": updated_user["id"], 
                "team_id": updated_user["team_id"], 
                "nickname": updated_user["nickname"], 
                "phone": updated_user["phone"],
                "email": updated_user["email"],
                "inviter_id": updated_user["inviter_id"],
                "role": updated_user["role"]
            }
            
            # Add additional fields for third-party users
            if hasattr(userinfo, 'user_type') and userinfo.user_type == "third_party":
                token_data.update({
                    "platform": getattr(userinfo, 'platform', ''),
                    "openid": getattr(userinfo, 'openid', ''),
                    "language": getattr(userinfo, 'language', 'en'),
                    "user_type": "third_party"
                })
            
            # Create new access token with updated data
            new_access_token = create_access_token(data=token_data)
            
            # Update Redis with new token
            redis_expiry_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
            redis.set(token_redis_key, new_access_token, ex=redis_expiry_seconds)
    
    # Prepare response data
    response_data = {"team_id": team_id_value}
    if new_access_token:
        response_data["access_token"] = new_access_token
    
    return response_success(response_data)

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
        sundry=login_data.sundry,
        nickname=login_data.nickname,
        position=login_data.position,
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


@router.post('/account_binding_with_three_parties', response_model=ResDictSchema)
async def account_binding_with_three_parties(user_return_data: AccountBindingWithThreeParties, userinfo: TokenData = Depends(get_current_user)):
    """
    Binds the current user account with a third-party platform account.

    Args:
        user_return_data (AccountBindingWithThreeParties): Contains platform binding data including platform name, openid, nickname, and avatar.
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.

    Returns:
        A success response with binding status message. If the account is already bound, returns a message indicating it's already bound.
        If binding is successful, creates a new record in user_three_parties table and updates user's nickname and avatar.
    """
    platform = user_return_data.platform
    openid = user_return_data.openid
    nickname = user_return_data.nickname
    avatar = user_return_data.avatar
    sundry = user_return_data.sundry

    user_id = userinfo.uid

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    new_data={
        'status':1
    }
    if not platform or platform.strip() == '':
        return response_error(get_language_content('third_party_login_platform_empty_return'))
    if not openid or openid.strip() == '':
        return response_error(get_language_content('third_party_login_openid_empty_return'))
    if nickname and nickname.strip():
        new_data['nickname'] = nickname
    if avatar and avatar.strip():
        new_data['avatar'] = avatar
        

    find_three_data= UserThreeParties().select_one(
        columns=['user_three_parties.id'], 
        joins=[
            ["left", "users", "user_three_parties.user_id = users.id"],
        ],
        conditions=[
            {'column': 'user_three_parties.user_id', 'value': user_id}, 
            {'column': 'user_three_parties.openid', 'value': openid}, 
            {'column': 'users.status', 'value': 1}
        ]
    )
    if find_three_data:
        msg_ok=get_language_content('the_current_account_has_been_bound')
        return response_success({'msg':msg_ok})

    have_user = UserThreeParties().select_one(
        columns=['user_three_parties.user_id'], 
        joins=[
            ["left", "users", "user_three_parties.user_id = users.id"],
        ],
        conditions=[
            {'column': 'user_three_parties.openid', 'value': openid}, 
            {'column': 'users.status', 'value': 1}
        ]
    )

    team_type_id = Teams().select_one(columns=['id'], conditions=[{'column': 'type', 'value': 2}])
    find_user_team_type_not_two = UserTeamRelations().select_one(
        columns=['id'], 
        conditions=[
            {'column': 'team_id', 'value': team_type_id['id']},
            {'column': 'user_id', 'value': user_id}
        ]
    )

    if have_user:
        have_user_id = have_user['user_id']
        user_info = Users().select_one(columns=['email','phone'], conditions=[{'column': 'id', 'value': have_user_id}])
        
        # Check if both email and phone are empty
        if not user_info or (not user_info.get('email') and not user_info.get('phone')):
            return response_error(get_language_content('user_contact_info_missing'))
        
        Users().update(
            [{'column': 'id', 'value': have_user_id}],
            {
                'status':3
            }
        )
        if find_user_team_type_not_two:
            UserTeamRelations().delete(
                [
                    {'column': 'user_id', 'value': have_user_id},
                    {'column': 'team_id', 'value': team_type_id['id']}
                ]
            )
        else:
            UserTeamRelations().update(
                [{'column': 'user_id', 'value': have_user_id}],
                {
                    'user_id':user_id
                }
            )
        UserThreeParties().update(
            [
                {'column': 'platform', 'value': platform},
                {'column': 'openid', 'value': openid}
            ],
            {
                'user_id':user_id
            }
        )
        msg_ok=get_language_content('binding_successful')
        return response_success({'msg':msg_ok})

    
    if find_user_team_type_not_two is None:
        user_team_data = {
            'user_id':user_id,
            'team_id':team_type_id,
            'role':2,
            'role_id':1,
            'inviter_id':0,
            'created_time': formatted_time
        }
        UserTeamRelations().insert(user_team_data)

    Users().update(
        [{'column': 'id', 'value': user_id}],
        new_data
    )

    
    data = {
        'user_id':user_id,
        'platform':platform,
        'openid':openid,
        'sundry':sundry,
        'created_at':formatted_time
    }
    UserThreeParties().insert(data)
    msg_ok=get_language_content('binding_successful')
    return response_success({'msg':msg_ok})

@router.post('/cancel_third_party_binding', response_model=ResDictSchema)
async def cancel_third_party_binding(request_data: OpenidList, userinfo: TokenData = Depends(get_current_user)):
    """
    Cancels third-party platform bindings for the current user.

    Args:
        request_data (OpenidList): Request data containing the list of openids to unbind from the current user account.
        userinfo (TokenData): The token data for the current authenticated user, obtained using the `get_current_user` dependency.

    Returns:
        A success response indicating the bindings have been cancelled, or an error response if any openid is not found.
    """
    user_id = userinfo.uid
    openid_list = request_data.openid_list
    
    if not openid_list or len(openid_list) == 0:
        return response_error(get_language_content('openid_list_empty'))
    
    # First, check if all openids exist for this user
    not_found_openids = []
    for openid in openid_list:
        existing_record = UserThreeParties().select_one(
            columns=['user_three_parties.id'],
            joins=[
                ["left", "users", "user_three_parties.user_id = users.id"],
            ],
            conditions=[
                {'column': 'user_three_parties.user_id', 'value': user_id},
                {'column': 'user_three_parties.openid', 'value': openid},
                {'column': 'users.status', 'value': 1}
            ]
        )
        if not existing_record:
            not_found_openids.append(openid)
    
    # If any openid is not found, return error
    if not_found_openids:
        return response_error(get_language_content('third_party_binding_not_found') + ': ' + ', '.join(not_found_openids))
    
    # Delete all bindings
    deleted_count = 0
    for openid in openid_list:
        try:
            UserThreeParties().delete([
                {'column': 'user_id', 'value': user_id},
                {'column': 'openid', 'value': openid}
            ])
            deleted_count += 1
        except Exception as e:
            return response_error(get_language_content('cancel_binding_failed') + f': {openid}')

     
    select_user_three_parties = UserThreeParties().select(
        columns=['id'],
        conditions=[
            {'column': 'user_id', 'value': user_id}
        ]
    )
    if not select_user_three_parties or len(select_user_three_parties) == 0:
        team_type_id = Teams().select_one(columns=['id'], conditions=[{'column': 'type', 'value': 2}])

        UserTeamRelations().delete(
            [
                {'column': 'user_id', 'value': user_id},
                {'column': 'team_id', 'value': team_type_id['id']}
            ]
        )

        find_user_team_type_not_two = UserTeamRelations().select_one(
            columns=['team_id','role','role_id','inviter_id'], 
            conditions=[
                {'column': 'user_id', 'value': user_id}
            ]
        )
        user_update_data = {
            "team_id":find_user_team_type_not_two['team_id'],
            "role":find_user_team_type_not_two['role'],
            "role_id":find_user_team_type_not_two['role_id'],
            "inviter_id":find_user_team_type_not_two['inviter_id']
        }

        Users().update(
            [{'column': 'id', 'value': user_id}],
            user_update_data
        )
        
    return response_success({
        'msg': get_language_content('cancel_binding_successful'),
        'deleted_count': deleted_count
    })



@router.post('/third_party_login_binding', response_model=ResThirdPartyLoginSchema)
async def third_party_login_binding(request: Request, login_data: ThirdPartyLoginData, userinfo: TokenData = Depends(get_current_user)):
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

    openid=login_data.openid
    user_id =userinfo.uid
    find_three_data= UserThreeParties().select_one(
        columns=['id'], 
        conditions=[
            {'column': 'user_id', 'value': user_id}, 
            {'column': 'openid', 'value': openid}
        ]
    )
    if not find_three_data:
        msg_ok=get_language_content('the_current_third_party_account_has_not_been_authorized_to_login')
        return response_error({'msg':msg_ok})

    
    # Authenticate or register third-party user
    user = authenticate_third_party_user_binding(
        platform=login_data.platform,
        openid=login_data.openid,
        sundry=login_data.sundry,
        position=login_data.position,
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


@router.post('/send_email_verification_code', response_model=ResDictSchema)
async def send_email_verification_code(request_data: ResetEmailData):
    """
    Send email verification code
    
    Args:
        request_data (dict): Request data containing email address
    
    Returns:
        A success response indicating the verification code has been sent, or an error response if the email is not found.
    """
    import random
    import string
    from core.smtp.emails_smtp import SMTPEmailSender
    
    email = request_data.email
    
    # Validate email format
    if not email or not is_valid_email(email):
        return response_error(get_language_content('email_format_incorrect'))
    
    # Check if user exists
    user = Users().get_user_by_email(email)
    if not user:
        return response_error(get_language_content('the_current_email_address_is_not_registered'))
    
    try:
        # Generate 6-digit alphanumeric verification code
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Store verification code in Redis with 15 minutes expiration and verification status
        redis_key = f"email_verification_code:{email}"
        verification_data = {
            'code': verification_code,
            'status': '0'  # 0: not verified, 1: verified
        }
        redis.set(redis_key, json.dumps(verification_data), ex=900)  # 15 minutes expiration
        
        # Get SMTP configuration and send email
        email_sender = SMTPEmailSender()
        
        # Send verification code email
        success, message = email_sender.send_password_reset_code_simple(
            to_email=email,
            code=verification_code,
            expire_minutes=15
        )
        
        if success:
            msg = get_language_content('verification_code_sent_successfully')
            return response_success({
                'msg': msg,
                'email': email
            })
        else:
            msg = get_language_content('email_sending_failed')
            return response_error(f"{msg}: {message}")
            
    except Exception as e:
        msg = get_language_content('an_error_occurred_while_sending_the_verification_code')
        return response_error(f"{msg}: {str(e)}")


@router.post('/verify_email_code', response_model=ResDictSchema)
async def verify_email_code(request_data: ResetVerificationCodeData):
    """
    Verify email verification code
    
    Args:
        request_data (dict): Request data containing email and verification code
    
    Returns:
        A success response if verification is successful, or an error response if verification fails.
    """
    email = request_data.email
    verification_code = request_data.verification_code
    
    # Validate email format
    if not email or not is_valid_email(email):
        return response_error(get_language_content('email_format_incorrect'))
    
    # Validate verification code is not empty
    if not verification_code or not verification_code.strip():
        return response_error(get_language_content('verification_code_cannot_be_empty'))
    
    # Check if user exists
    user = Users().get_user_by_email(email)
    if not user:
        return response_error(get_language_content('the_current_email_address_is_not_registered'))
    
    try:
        # Get verification data from Redis
        redis_key = f"email_verification_code:{email}"
        stored_data = redis.get(redis_key)
        
        if not stored_data:
            return response_error(get_language_content('verification_code_expired_or_not_exist'))
        
        # Parse stored verification data
        try:
            verification_data = json.loads(str(stored_data, 'utf-8'))
            stored_code = verification_data.get('code')
        except (json.JSONDecodeError, KeyError):
            return response_error(get_language_content('verification_code_expired_or_not_exist'))
        
        # Compare verification codes
        if stored_code != verification_code.strip():
            return response_error(get_language_content('verification_code_incorrect'))
        
        # Verification successful, update status to verified (1) instead of deleting
        verification_data['status'] = '1'
        redis.set(redis_key, json.dumps(verification_data), ex=900)  # Keep same expiration time
        
        msg = get_language_content('email_verification_successful')
        return response_success({
            'msg': msg,
            'email': email,
            'verified': True
        })
        
    except Exception as e:
        msg = get_language_content('email_verification_failed')
        return response_error(f"{msg}: {str(e)}")


@router.post('/reset_password', response_model=ResDictSchema)
async def reset_password(reset_data: ResetPasswordData):
    """
    Reset user password
    
    Args:
        reset_data (ResetPasswordData): Reset password data containing email, new password and confirm password
    
    Returns:
        A success response if password reset is successful, or an error response if reset fails.
    """
    email = reset_data.email
    password = reset_data.password
    confirm_password = reset_data.confirm_password
    
    # Validate email format
    if not email or not is_valid_email(email):
        return response_error(get_language_content('email_format_incorrect'))
    
    # Validate password is not empty
    if not password or not password.strip():
        return response_error(get_language_content('password_cannot_be_empty'))
    
    # Validate confirm password is not empty
    if not confirm_password or not confirm_password.strip():
        return response_error(get_language_content('confirm_password_cannot_be_empty'))
    
    # Validate password and confirm password match
    if password != confirm_password:
        return response_error(get_language_content('passwords_do_not_match'))
    
    # Check if user exists
    user = Users().get_user_by_email(email)
    if not user:
        return response_error(get_language_content('the_current_email_address_is_not_registered'))
    
    try:
        # Check if email verification is completed
        redis_key = f"email_verification_code:{email}"
        stored_data = redis.get(redis_key)
        
        if not stored_data:
            return response_error(get_language_content('email_verification_not_completed'))
        
        # Parse stored verification data
        try:
            verification_data = json.loads(str(stored_data, 'utf-8'))
            verification_status = verification_data.get('status')
        except (json.JSONDecodeError, KeyError):
            return response_error(get_language_content('verification_status_invalid'))
        
        # Check if verification status is successful (1)
        if verification_status != '1':
            return response_error(get_language_content('email_verification_not_completed'))
        
        # Generate password salt and encrypted password following register_user method logic
        password_salt = str(int(datetime.now().timestamp()))
        password_with_salt = hashlib.md5((hashlib.md5(password.encode()).hexdigest() + password_salt).encode()).hexdigest()
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update user password
        update_data = {
            'password': password_with_salt,
            'password_salt': password_salt,
            'updated_time': formatted_time
        }
        
        result = Users().update(
            [{'column': 'id', 'value': user['id']}],
            update_data
        )
        
        SQLDatabase.commit()
        SQLDatabase.close()
        
        if result:
            # Password reset successful, delete verification data from Redis
            redis.delete(redis_key)
            
            msg = get_language_content('password_reset_successful')
            return response_success({
                'msg': msg,
                'email': email
            })
        else:
            msg = get_language_content('password_reset_failed')
            return response_error(msg)
            
    except Exception as e:
        msg = get_language_content('password_reset_failed')
        return response_error(f"{msg}: {str(e)}")


@router.post('/update_profile', response_model=ResDictSchema)
async def update_profile(profile_data: UpdateProfileData, userinfo: TokenData = Depends(get_current_user)):
    """
    Update user profile (nickname and position)
    
    Args:
        profile_data (UpdateProfileData): Profile data containing nickname and optional position
        userinfo (TokenData): The token data for the current authenticated user
    
    Returns:
        A success response if profile update is successful, or an error response if update fails.
    """
    nickname = profile_data.nickname
    position = profile_data.position

    team_id = userinfo.team_id
    user_id = userinfo.uid
    
    # Validate nickname is not empty
    if not nickname or not nickname.strip():
        return response_error(get_language_content('register_nickname_empty'))
    
    # Validate nickname length
    if len(nickname.encode('utf-8')) > 50:
        return response_error(get_language_content('register_nickname_long'))
    
    try:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Prepare update data
        update_data = {
            'nickname': nickname.strip(),
            'updated_time': formatted_time
        }
        
        # Only update position if it's provided and not empty
        if position is not None and position.strip():
            UserTeamRelations().update_user_position(user_id, team_id, position)
            # update_data['position'] = position.strip()
        
        # Update user profile
        result = Users().update(
            data=update_data,
            conditions=[{'column': 'id', 'value': user_id}]
        )
        
        SQLDatabase.commit()
        SQLDatabase.close()
        
        if result:
            # Update Redis cache with new user info
            updated_user_info = Users().select_one(
                columns=['nickname'], 
                conditions=[{'column': 'id', 'value': user_id}]
            )
            
            # Initialize user_cache with default values
            user_cache = {'nickname': updated_user_info['nickname'], 'position': ''}
            
            # Update Redis cache if user info exists
            if updated_user_info:
                redis_key = f"user_info:{user_id}"
                try:
                    # Get existing cache data
                    cached_data = redis.get(redis_key)
                    if cached_data:
                        user_cache = json.loads(str(cached_data, 'utf-8'))
                        user_cache['nickname'] = updated_user_info['nickname']
                    
                    # Get position from user_team_relations
                    get_user_team_relation = UserTeamRelations().get_user_team_relation(user_id, team_id)
                    if get_user_team_relation and get_user_team_relation.get('position'):
                        user_cache['position'] = get_user_team_relation['position']
                    else:
                        user_cache['position'] = ''
                    
                    # Update cache with 1 hour expiration
                    redis_expiry_seconds = ACCESS_TOKEN_EXPIRE_MINUTES * 60
                    redis.set(redis_key, json.dumps(user_cache), ex=redis_expiry_seconds)
                except Exception as cache_error:
                    # Cache update failed, but profile update succeeded
                    pass
            
            msg = get_language_content('profile_updated_successfully')
            return response_success({
                'msg': msg,
                'nickname': updated_user_info['nickname'],
                'position': user_cache.get('position', '')
            })
        else:
            msg = get_language_content('profile_update_failed')
            return response_error(msg)
            
    except Exception as e:
        # Log the actual error for debugging
        # print(f"Profile update error: {str(e)}")
        msg = get_language_content('profile_update_failed')
        return response_error(msg)


@router.post('/change_password', response_model=ResDictSchema)
async def change_password(password_data: ChangePasswordData, userinfo: TokenData = Depends(get_current_user)):
    """
    Change user password
    
    Args:
        password_data (ChangePasswordData): Password data containing old password, new password and confirm password
        userinfo (TokenData): The token data for the current authenticated user
    
    Returns:
        A success response if password change is successful, or an error response if change fails.
    """
    old_password = password_data.old_password
    new_password = password_data.new_password
    confirm_password = password_data.confirm_password
    
    # Validate old password is not empty
    if not old_password or not old_password.strip():
        return response_error(get_language_content('old_password_cannot_be_empty'))
    
    # Validate new password is not empty
    if not new_password or not new_password.strip():
        return response_error(get_language_content('new_password_cannot_be_empty'))
    
    # Validate confirm password is not empty
    if not confirm_password or not confirm_password.strip():
        return response_error(get_language_content('confirm_password_cannot_be_empty'))
    
    # Validate new password and confirm password match
    if new_password != confirm_password:
        return response_error(get_language_content('new_passwords_do_not_match'))
    
    try:
        # Get current user data
        uid = userinfo.uid
        # Get user info (works for both regular and third-party users)
        user_info = get_uid_user_info(uid)
        
        # Verify old password
        old_password_with_salt = hashlib.md5(
            (hashlib.md5(old_password.encode()).hexdigest() + user_info['password_salt']).encode()
        ).hexdigest()
        
        if old_password_with_salt != user_info['password']:
            return response_error(get_language_content('old_password_incorrect'))
        
        # Generate new password salt and encrypted password
        new_password_salt = str(int(datetime.now().timestamp()))
        new_password_with_salt = hashlib.md5(
            (hashlib.md5(new_password.encode()).hexdigest() + new_password_salt).encode()
        ).hexdigest()
        
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Update user password
        update_data = {
            'password': new_password_with_salt,
            'password_salt': new_password_salt,
            'updated_time': formatted_time
        }
        
        result = Users().update(
            [{'column': 'id', 'value': userinfo.uid}],
            update_data
        )
        
        SQLDatabase.commit()
        SQLDatabase.close()
        
        if result:
            msg = get_language_content('password_changed_successfully')
            return response_success({
                'msg': msg
            })
        else:
            msg = get_language_content('password_change_failed')
            return response_error(msg)
            
    except Exception as e:
        msg = get_language_content('password_change_failed')
        return response_error(f"{msg}")


@router.post('/switch_member_role', response_model=ResDictSchema)
async def switch_member_role(role_data: SwitchMemberRoleData, userinfo: TokenData = Depends(get_current_user)):
    """
    Switch team member's role (Admin only)
    
    Args:
        role_data (SwitchMemberRoleData): Role data containing user_id and role_id
        userinfo (TokenData): The token data for the current authenticated user
    
    Returns:
        A success response if role switch is successful, or an error response if switch fails.
    """
    target_user_id = role_data.user_id
    role = role_data.role
    new_role_id = role_data.role_id
    current_user_id = userinfo.uid
    current_team_id = userinfo.team_id
    
    # Validate required parameters
    if not target_user_id or target_user_id <= 0:
        return response_error(get_language_content('invalid_user_id'))
    
    # Validate role parameter
    if role not in [1, 2]:
        return response_error(get_language_content('role_must_be_1_or_2'))
    
    # Validate role_id based on role value
    if role == 1:
        # For admin role, role_id should be None/empty (set to None even if 0 is provided)
        new_role_id = None
    elif role == 2:
        # For regular role, role_id is required
        if new_role_id is None or new_role_id <= 0:
            return response_error(get_language_content('role_id_required_for_regular_role'))
    
    try:
        # Check if current user is admin (role = 1) in the current team
        current_user_relation = UserTeamRelations().get_user_team_relation(current_user_id, current_team_id)
        if not current_user_relation or current_user_relation.get('role') != 1:
            return response_error(get_language_content('only_admin_can_switch_member_roles'))
        
        # Check if user is trying to modify their own role from admin to regular user
        if target_user_id == current_user_id and current_user_relation.get('role') == 1 and role == 2:
            # Count secure admins (exclude users with default password value)
            secure_admin_ids = UserTeamRelations().get_secure_admin_user_ids(current_team_id)
            if target_user_id in secure_admin_ids and len(secure_admin_ids) <= 1:
                return response_error(get_language_content('cannot_modify_last_admin_role'))
        
        # Check if target user exists in the same team
        target_user_relation = UserTeamRelations().get_user_team_relation(target_user_id, current_team_id)
        if not target_user_relation:
            return response_error(get_language_content('target_user_not_in_current_team'))
        
        # Check if target user is admin (role = 1) and ensure at least one admin remains
        # Skip this check if we already checked it for self-modification above
        if target_user_relation.get('role') == 1 and target_user_id != current_user_id and role == 2:
            # Count secure admins (exclude users with default password value)
            secure_admin_ids = UserTeamRelations().get_secure_admin_user_ids(current_team_id)
            if target_user_id in secure_admin_ids and len(secure_admin_ids) <= 1:
                return response_error(get_language_content('cannot_modify_last_admin_role'))
        
        # Validate role_id if it's provided (for role = 2)
        role_info = None
        if role == 2 and new_role_id is not None:
            role_info = Roles().get_role_by_id(new_role_id)
            if not role_info:
                return response_error(get_language_content('role_not_found'))
            
            # Check if role belongs to current team or is built-in role
            if role_info.get('team_id') != current_team_id and role_info.get('built_in') != 1:
                return response_error(get_language_content('role_not_available_for_current_team'))
        
        # Update user's role in user_team_relations
        update_data = {
            'role': role,
            'role_id': new_role_id
        }
        result = UserTeamRelations().update(
            conditions=[
                {'column': 'user_id', 'value': target_user_id},
                {'column': 'team_id', 'value': current_team_id}
            ],
            data=update_data
        )
        
        SQLDatabase.commit()
        SQLDatabase.close()
        if result:
            # Clear Redis cache for the user whose role was switched
            try:
                # Get information of the user whose role was switched
                target_user_info = get_uid_user_info(target_user_id)
                if target_user_info:
                    # Determine user type and set Redis key
                    password = target_user_info.get('password', '')
                    redis_key = None
                    
                    # Determine password type
                    if password == 'nexus_ai123456':
                        # Regular user
                        redis_key = f"access_token:{target_user_id}"
                    elif password == 'third_party_default':
                        # Third-party user
                        redis_key = f"third_party_access_token:{target_user_id}"
                    else:
                        # Other regular users
                        redis_key = f"access_token:{target_user_id}"
                    
                    # Check if the key exists in Redis, delete if it exists
                    if redis.exists(redis_key):
                        redis.delete(redis_key)
            except Exception as e:
                # Cache clearing failure should not affect the main process
                print(f"Failed to clear user Redis cache: {e}")
            
            msg = get_language_content('member_role_switched_successfully')
            return response_success({
                'msg': msg,
                'user_id': target_user_id,
                'role': role,
                'new_role_id': new_role_id,
                'role_name': role_info.get('name', '') if role_info is not None else ('Administrator' if role == 1 else '')
            })
        else:
            msg = get_language_content('member_role_switch_failed')
            return response_error(msg)
            
    except Exception as e:
        msg = get_language_content('member_role_switch_failed')
        return response_error(msg)