from typing import Dict, Any, Optional

from core.database import MySQL


class ThirdPartyUsers(MySQL):
    """
    A class that extends MySQL to manage operations on the third_party_users table.
    """
    table_name = "third_party_users"
    """
    Indicates whether the `third_party_users` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

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

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by user ID.

        :param user_id: The ID of the user.
        :return: The user data if found, None otherwise.
        """
        user = self.select_one(
            columns='*',
            conditions=[
                {'column': 'id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ]
        )
        return user

    def create_or_update_user(self, platform: str, openid: str, nickname: str = None, 
                             avatar: str = None, language: str = 'en', 
                             last_login_ip: str = None) -> int:
        """
        Create a new third-party user or update existing user.

        :param platform: The third-party platform identifier.
        :param openid: The user's openid on the platform.
        :param nickname: The user's nickname (optional).
        :param avatar: The user's avatar URL (optional).
        :param language: The user's language preference.
        :param last_login_ip: The user's last login IP.
        :return: The user ID.
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
                'platform': platform,
                'openid': openid,
                'nickname': nickname,
                'avatar': avatar,
                'language': language,
                'last_login_ip': last_login_ip,
                'last_login_time': formatted_time,
                'status': 1
            }
            
            # Remove None values
            user_data = {k: v for k, v in user_data.items() if v is not None}
            
            return self.insert(user_data)

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
            raise ValueError(f"Third-party user with ID {user_id} not found") 