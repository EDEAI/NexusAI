from typing import Dict, Any, Optional

from core.database import MySQL


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
        user = self.select_one(
            columns='*',
            conditions=[
                {'column': 'platform', 'value': platform},
                {'column': 'openid', 'value': openid},
                {'column': 'status', 'value': 1}
            ]
        )
        return user

    def create_or_update_third_party_user(self, platform: str, openid: str, nickname: str = None, 
                                          avatar: str = None, language: str = 'en', 
                                          last_login_ip: str = None):
        """
        Create a new third-party user or update existing user information.

        :param platform: The third-party platform identifier.
        :param openid: The user's openid on the platform.
        :param nickname: The user's nickname (optional).
        :param avatar: The user's avatar URL (optional).
        :param language: The user's language preference.
        :param last_login_ip: The user's last login IP.
        :return: The user ID if successful, None otherwise.
        """
        # Check if user already exists
        existing_user = self.get_user_by_platform_and_openid(platform, openid)
        
        if existing_user:
            # Update existing user
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            update_data = {
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time
            }
            
            # Update optional fields if provided
            if nickname is not None:
                update_data['nickname'] = nickname
            if avatar is not None:
                update_data['avatar'] = avatar
            if language is not None:
                update_data['language'] = language
                
            self.update(
                [{'column': 'id', 'value': existing_user['id']}],
                update_data
            )
            return existing_user['id']
        else:
            # Create new user
            from datetime import datetime
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            
            user_data = {
                'team_id': 0,  # Third-party users are not associated with any team
                'role': 2,     # Default role for third-party users
                'inviter_id': 0,
                'nickname': nickname or f'{platform}_user',
                'phone': None,
                'email': None,
                'password': 'third_party_default',
                'password_salt': 'third_party_salt',
                'avatar': avatar,
                'created_time': formatted_time,
                'language': language,
                'platform': platform,
                'openid': openid,
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time,
                'status': 1
            }
            
            user_id = self.insert(user_data)
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
