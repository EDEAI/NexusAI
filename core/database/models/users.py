from typing import Dict, Any, Optional, Union

from core.database import MySQL
from core.database.models.user_team_relations import UserTeamRelations
from core.database.models.user_three_parties import UserThreeParties
from core.database.models.teams import Teams



class Users(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    table_name = "users"
    """
    Indicates whether the `users` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def search_my_team_all_agents(self, uid: int, level: int = 0, user_ids=None, all_agents=None):
        if level == 0:
            # 在初始调用时定义并初始化 all_agents 列表
            all_agents = []
            conditions = [
                {'column': 'id', 'value': uid},
                {'column': 'status', 'value': 1},
            ]
        else:
            conditions = [
                {'column': 'status', 'value': 1},
                {"column": "inviter_id", "op": "in", "value": user_ids}
            ]

        level += 1  # 增加层级深度信息

        # 当前层级查询
        datasets = self.select(
            columns=['id AS user_id'],
            conditions=conditions,
        )

        if datasets:
            # 提取 user_id 生成新的列表
            user_id = [item['user_id'] for item in datasets]
            all_agents = all_agents + user_id
            # 递归调用并返回结果
            return self.search_my_team_all_agents(uid, level, user_id, all_agents)
        else:
            # 返回结果
            filtered_list = [x for x in all_agents if x != uid]
            return filtered_list

    # Get the role of the user
    def get_user_id_role(self, user_id: int) -> bool:
        role = self.select_one(columns="*", conditions=[{'column': 'id', 'value': user_id}])
        print(role)
        if role['role'] != 1:
            return False
        return True

    def get_user_language(self, user_id: int) -> str:
        """
        Get the current language of the user by user ID.

        :param user_id: The ID of the user.
        :return: The current language of the user.
        """
        user = self.select_one(columns=["language"], conditions={'column': 'id', 'value': user_id})
        if user:
            return user['language']
        else:
            raise ValueError(f"User with ID {user_id} not found")

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        user = self.select_one(
            columns=['team_id', 'id', 'nickname'],
            conditions=[
                {'column': 'id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ]
        )
        return user

    def get_user_by_platform_and_openid(self, platform: str, openid: str) -> Optional[Dict[str, Any]]:
        """
        Get user by platform and openid.

        :param platform: The third-party platform identifier.
        :param openid: The user's openid on the platform.
        :return: The user data if found, None otherwise.
        """
        # user = self.select_one(
        #     columns='*',
        #     conditions=[
        #         {'column': 'platform', 'value': platform},
        #         {'column': 'openid', 'value': openid},
        #         {'column': 'status', 'value': 1}
        #     ]
        # )
        user_three_parties_info = UserThreeParties().select_one(
            columns=['user_three_parties.user_id AS id','user_three_parties.platform','user_three_parties.openid'],
            joins=[
                ["left", "users", "user_three_parties.user_id = users.id"],
            ],
            conditions=[
                {'column': 'user_three_parties.platform', 'value': platform},
                {'column': 'user_three_parties.openid', 'value': openid},
                {'column': 'users.status', 'value': 1}
            ]
        )
        return user_three_parties_info

    def create_or_update_third_party_user(self, platform: str, openid: str, sundry: Union[str, int, None] = None, nickname: str = None, position: str = None,
                                          avatar: str = None, language: str = 'en', 
                                          last_login_ip: str = None, phone: str = None, email: str = None):
        """
        Create a new third-party user or update existing user information.

        :param platform: The third-party platform identifier.
        :param openid: The user's openid on the platform.
        :param nickname: The user's nickname (optional).
        :param avatar: The user's avatar URL (optional).
        :param language: The user's language preference.
        :param last_login_ip: The user's last login IP.
        :param phone: The user's phone number (optional).
        :param email: The user's email address (optional).
        :return: The user ID if successful, None otherwise.
        """
        user_id = None
        if email:
            user_id = self.get_user_id_by_email(email)
        elif phone:
            user_id = self.get_user_id_by_phone(phone)
        # Step 1: Try to find user by platform and openid
        existing_user = self.get_user_by_platform_and_openid(platform, openid)
        if existing_user:
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time
            }
            if nickname and nickname.strip():
                update_data['nickname'] = nickname
            # if position and position.strip():
            #     update_data['position'] = position
            if avatar and avatar.strip():
                update_data['avatar'] = avatar
            # if language and language.strip():
            #     update_data['language'] = language
            # if phone:
            #     update_data['phone'] = phone
            # if email:
            #     update_data['email'] = email
            if user_id:
                new_data = {
                    # 'platform':existing_user['platform'],
                    # 'openid':existing_user['openid'],
                    'last_login_ip':last_login_ip,
                    'last_login_time': formatted_time
                }
                if nickname and nickname.strip():
                    new_data['nickname'] = nickname
                # if position and position.strip():
                #     new_data['position'] = position
                if avatar and avatar.strip():
                    new_data['avatar'] = avatar
                user_info = self.select_one(columns=['id','phone','email'], conditions=[{'column': 'id', 'value': user_id}, {'column': 'status', 'value': 1}])

                # if phone is not None and user_info['phone'] is None:
                if phone and phone.strip() and user_info['phone'] is None:
                    new_data['phone'] = phone
                if email and email.strip()  and user_info['email'] is None:
                    new_data['email'] = email
                if user_id != existing_user['id']:
                    self.update(
                        [{'column': 'id', 'value': existing_user['id']}],
                        {
                            'status':3
                        }
                    )
                    team_type_id = Teams().select_one(columns=['id'], conditions=[{'column': 'type', 'value': 2}])
                    find_user_team_type_not_two = UserTeamRelations().select_one(
                        columns=['id'], 
                        conditions=[
                            {'column': 'team_id', 'value': team_type_id['id']},
                            {'column': 'user_id', 'value': user_id}
                        ]
                    )
                    if find_user_team_type_not_two:
                        UserTeamRelations().delete(
                            [
                                {'column': 'user_id', 'value': existing_user['id']},
                                {'column': 'team_id', 'value': team_type_id['id']}
                            ]
                        )

                team_id = UserTeamRelations().select_one(columns=['team_id'], conditions=[{'column': 'user_id', 'value': existing_user['id']}])

                UserTeamRelations().update(
                    [{'column': 'user_id', 'value': existing_user['id']}],
                    {
                        'user_id':user_id
                    }
                )
                
                self.update(
                    [{'column': 'id', 'value': user_id}],
                    new_data
                )
                if position and position.strip():
                    from api.utils.auth import get_uid_user_info
                    userInfos=get_uid_user_info(user_id)
                    UserTeamRelations().update(
                        [{'column': 'user_id', 'value': user_id},{'column': 'team_id', 'value': userInfos['team_id']}],
                        {
                            'position':position
                        }
                    )
                UserThreeParties().update(
                    [{'column': 'user_id', 'value': existing_user['id']}],
                    {
                        'user_id':user_id,
                        'updated_at': formatted_time
                    }
                )

                if sundry is not None and sundry != '' and sundry.strip() != '':
                    UserThreeParties().update(
                        [{'column': 'user_id', 'value': existing_user['id']}],
                        {
                            'sundry':sundry,
                            'updated_at': formatted_time
                        }
                    )

                return user_id
            else:
                if sundry is not None and sundry != '' and sundry.strip() != '':
                    UserThreeParties().update(
                        [{'column': 'user_id', 'value': existing_user['id']}],
                        {
                            'sundry':sundry,
                            'updated_at': formatted_time
                        }
                    )

                self.update(
                    [{'column': 'id', 'value': existing_user['id']}],
                    update_data
                )

                if position and position.strip():
                    from api.utils.auth import get_uid_user_info
                    userInfos=get_uid_user_info(existing_user['id'])
                    UserTeamRelations().update(
                        [{'column': 'user_id', 'value': existing_user['id']},{'column': 'team_id', 'value': userInfos['team_id']}],
                        {
                            'position':position
                        }
                    )
                
                return existing_user['id']

        # Step 2: Try to find user by email or phone
        
        
        if user_id:
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            team_id = Teams().get_personal_workspace_team_id()

            update_data = {
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time
            }
            if nickname and nickname.strip():
                update_data['nickname'] = nickname
            # if position and position.strip():
            #     update_data['position'] = position
            if avatar and avatar.strip():
                update_data['avatar'] = avatar
            # if language and language.strip():
            #     update_data['language'] = language
            if phone and phone.strip():
                update_data['phone'] = phone
            if email and email.strip():
                update_data['email'] = email
            self.update(
                [{'column': 'id', 'value': user_id}],
                update_data
            )

            if position and position.strip():
                from api.utils.auth import get_uid_user_info
                userInfos=get_uid_user_info(user_id)
                UserTeamRelations().update(
                    [{'column': 'user_id', 'value': user_id},{'column': 'team_id', 'value': userInfos['team_id']}],
                    {
                        'position':position
                    }
                )
            
            UserThreeParties().insert(
                {
                    'user_id':user_id,
                    'openid':openid,
                    'platform':platform,
                    'sundry':sundry,
                    'created_at': formatted_time
                }
            )
            team_find = UserTeamRelations().select(
                columns=['id'],
                conditions=[
                    {'column': 'user_id', 'value': user_id},
                    {'column': 'team_id', 'value': team_id}
                ]
            )
            if not team_find or len(team_find) == 0:
                user_team_data = {
                    'user_id':user_id,
                    'team_id':team_id,
                    'role_id':1,
                    'created_time': formatted_time
                }
                UserTeamRelations().insert(user_team_data)

            return user_id
        else:
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            user_data = {
                'team_id': 1,  # Third-party users are not associated with any team
                'role': 2,     # Default role for third-party users
                'role_id': 1,
                'inviter_id': 0,
                'nickname': nickname or f'{platform}_user',
                # 'position': position,
                'phone': phone,
                'email': email,
                'password': 'third_party_default',
                'password_salt': 'third_party_salt',
                'avatar': avatar,
                'created_time': formatted_time,
                'language': language,
                # 'platform': platform,
                # 'openid': openid,
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time,
                'status': 1
            }
            # Get the personal workspace team id and insert it into the user-team association table
            user_id = self.insert(user_data)

            UserThreeParties().insert(
                {
                    'user_id':user_id,
                    'openid':openid,
                    'platform':platform,
                    'sundry':sundry,
                    'created_at': formatted_time
                }
            )

            team_id = Teams().get_personal_workspace_team_id()
            user_team_data = {
                'user_id':user_id,
                'team_id':team_id,
                'position':position,
                'role':2,
                'role_id': 1,
                'inviter_id': 0,
                'created_time': formatted_time
            }
            UserTeamRelations().insert(user_team_data)
            user_update_data = {
                'team_id':team_id
            }
            self.update(
                [{'column': 'id', 'value': user_id}],
                user_update_data
            )
            return user_id

    def update_login_info(self, user_id: int, last_login_ip: str):
        """
        Update user's login information.

        :param user_id: The ID of the user.
        :param last_login_ip: The user's last login IP.
        """
        from datetime import datetime
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        self.update(
            [{'column': 'id', 'value': user_id}],
            {
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time
            }
        )

    def get_user_id_by_phone(self, phone: str) -> Optional[int]:
        """
        Query and get the user ID by phone number.

        :param phone: The user's phone number.
        :return: The user ID if found, otherwise None.
        """
        user = self.select_one(
            columns=["id"],
            conditions=[
                {"column": "phone", "value": phone},
                {"column": "status", "value": 1}
            ]
        )
        if user:
            return user["id"]
        return None

    def get_user_id_by_email(self, email: str) -> Optional[int]:
        """
        Query and get the user ID by email address.

        :param email: The user's email address.
        :return: The user ID if found, otherwise None.
        """
        user = self.select_one(
            columns=["id"],
            conditions=[
                {"column": "email", "value": email},
                {"column": "status", "value": 1}
            ]
        )
        if user:
            return user["id"]
        return None

    def create_or_update_third_party_user_binding(self, platform: str, openid: str, sundry: Union[str, int, None] = None, nickname: str = None,position: str = None, 
                                          avatar: str = None, language: str = 'en', 
                                          last_login_ip: str = None, phone: str = None, email: str = None):
        """
        Create a new third-party user or update existing user information.

        :param platform: The third-party platform identifier.
        :param openid: The user's openid on the platform.
        :param nickname: The user's nickname (optional).
        :param avatar: The user's avatar URL (optional).
        :param language: The user's language preference.
        :param last_login_ip: The user's last login IP.
        :param phone: The user's phone number (optional).
        :param email: The user's email address (optional).
        :return: The user ID if successful, None otherwise.
        """
        user_id = None
        if email:
            user_id = self.get_user_id_by_email(email)
        elif phone:
            user_id = self.get_user_id_by_phone(phone)
        # Step 1: Try to find user by platform and openid
        existing_user = self.get_user_by_platform_and_openid(platform, openid)
        if existing_user:
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

            update_data = {
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time
            }
            if nickname and nickname.strip():
                update_data['nickname'] = nickname
            # if position and position.strip():
            #     update_data['position'] = position
            if avatar and avatar.strip():
                update_data['avatar'] = avatar
            # if language and language.strip():
            #     update_data['language'] = language
            # if phone:
            #     update_data['phone'] = phone
            # if email:
            #     update_data['email'] = email
            if user_id:
                new_data = {
                    # 'platform':existing_user['platform'],
                    # 'openid':existing_user['openid'],
                    'last_login_ip':last_login_ip,
                    'last_login_time': formatted_time
                }
                if nickname and nickname.strip():
                    new_data['nickname'] = nickname
                # if position and position.strip():
                #     new_data['position'] = position
                if avatar and avatar.strip():
                    new_data['avatar'] = avatar
                user_info = self.select_one(columns=['id','phone','email'], conditions=[{'column': 'id', 'value': user_id}, {'column': 'status', 'value': 1}])

                if phone and phone.strip() and user_info['phone'] is None:
                    new_data['phone'] = phone
                if email and email.strip() and user_info['email'] is None:
                    new_data['email'] = email
                if user_id != existing_user['id']:
                    self.update(
                        [{'column': 'id', 'value': existing_user['id']}],
                        {
                            'status':3
                        }
                    )
                    team_type_id = Teams().select_one(columns=['id'], conditions=[{'column': 'type', 'value': 2}])
                    find_user_team_type_not_two = UserTeamRelations().select_one(
                        columns=['id'], 
                        conditions=[
                            {'column': 'team_id', 'value': team_type_id['id']},
                            {'column': 'user_id', 'value': user_id}
                        ]
                    )
                    if find_user_team_type_not_two:
                        UserTeamRelations().delete(
                            [
                                {'column': 'user_id', 'value': existing_user['id']},
                                {'column': 'team_id', 'value': team_type_id['id']}
                            ]
                        )

                team_id = UserTeamRelations().select_one(columns=['team_id'], conditions=[{'column': 'user_id', 'value': existing_user['id']}])

                UserTeamRelations().update(
                    [{'column': 'user_id', 'value': existing_user['id']}],
                    {
                        'user_id':user_id
                    }
                )
                
                self.update(
                    [{'column': 'id', 'value': user_id}],
                    new_data
                )

                if position and position.strip():
                    from api.utils.auth import get_uid_user_info
                    userInfos=get_uid_user_info(user_id)
                    UserTeamRelations().update(
                        [{'column': 'user_id', 'value': user_id},{'column': 'team_id', 'value': userInfos['team_id']}],
                        {
                            'position':position
                        }
                    )
                if sundry is not None and sundry != '' and sundry.strip() != '':
                    UserThreeParties().update(
                        [{'column': 'user_id', 'value': existing_user['id']}],
                        {
                            'sundry':sundry,
                            'updated_at': formatted_time
                        }
                    )

                UserThreeParties().update(
                    [{'column': 'user_id', 'value': existing_user['id']}],
                    {
                        'user_id':user_id,
                        'updated_at': formatted_time
                    }
                )
                return user_id
            else:
                if sundry is not None and sundry != '' and sundry.strip() != '':
                    UserThreeParties().update(
                        [{'column': 'user_id', 'value': existing_user['id']}],
                        {
                            'sundry':sundry,
                            'updated_at': formatted_time
                        }
                    )

                self.update(
                    [{'column': 'id', 'value': existing_user['id']}],
                    update_data
                )

                if position and position.strip():
                    from api.utils.auth import get_uid_user_info
                    userInfos=get_uid_user_info(existing_user['id'])
                    UserTeamRelations().update(
                        [{'column': 'user_id', 'value': existing_user['id']},{'column': 'team_id', 'value': userInfos['team_id']}],
                        {
                            'position':position
                        }
                    )

                return existing_user['id']
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        user = self.select_one(
            columns=['id'],
            conditions=[
                {'column': 'email', 'value': email},
                {'column': 'status', 'value': 1}
            ]
        )
        return user