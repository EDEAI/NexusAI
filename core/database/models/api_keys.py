import secrets
import string
from typing import Any, Dict, Optional
from datetime import datetime

from core.database import MySQL


class ApiKeys(MySQL):
    """
    A class that extends MySQL to manage operations on the api_keys table.
    """
    table_name = "api_keys"
    """
    Indicates whether the `api_keys` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def generate_api_key(self) -> str:
        """
        Generate a new API key with format 'app-' followed by 24 random characters.
        
        :return: A new API key string.
        """
        # Generate 24 random characters (uppercase, lowercase, and digits)
        random_chars = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(24))
        return f"app-{random_chars}"

    def create_api_key(self, app_id: int, user_id: int) -> Dict[str, Any]:
        """
        Create a new API key for an app.
        
        :param app_id: The ID of the app.
        :param user_id: The ID of the user creating the API key.
        :return: A dictionary containing the created API key information.
        """
        # Generate a unique API key
        api_key = self.generate_api_key()
        
        # Check if the key already exists (very unlikely but possible)
        while self.select_one(columns=['id'], conditions=[{'column': 'key', 'value': api_key}]):
            api_key = self.generate_api_key()
        
        # Create the API key record
        key_data = {
            'app_id': app_id,
            'user_id': user_id,
            'key': api_key,
            'status': 1,  # 1: active
            'created_time': datetime.now()
        }
        
        key_id = self.insert(key_data)
        
        # Return the created API key information
        return {
            'id': key_id,
            'app_id': app_id,
            'user_id': user_id,
            'key': api_key,
            'status': 1,
            'last_used_time': None,
            'created_time': key_data['created_time'],
            'updated_time': None
        }

    def get_api_keys_by_app_and_user(self, app_id: int, user_id: int) -> list:
        """
        Get all API keys for a specific app created by a specific user.
        
        :param app_id: The ID of the app.
        :param user_id: The ID of the user.
        :return: A list of API key dictionaries.
        """
        return self.select(
            columns=[
                'id', 'app_id', 'user_id', 'key', 'status', 
                'last_used_time', 'created_time', 'updated_time'
            ],
            conditions=[
                {'column': 'app_id', 'value': app_id},
                {'column': 'user_id', 'value': user_id},
                {'column': 'status', 'value': 1}
            ],
            order_by='created_time DESC'
        )

    def get_api_key_by_id(self, key_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an API key by its ID, ensuring it belongs to the specified user.
        
        :param key_id: The ID of the API key.
        :param user_id: The ID of the user.
        :return: A dictionary containing the API key information or None if not found.
        """
        return self.select_one(
            columns=[
                'id', 'app_id', 'user_id', 'key', 'status', 
                'last_used_time', 'created_time', 'updated_time'
            ],
            conditions=[
                {'column': 'id', 'value': key_id},
                {'column': 'user_id', 'value': user_id}
            ]
        )

    def update_api_key_status(self, key_id: int, user_id: int, status: int) -> bool:
        """
        Update the status of an API key, ensuring it belongs to the specified user.
        
        :param key_id: The ID of the API key.
        :param user_id: The ID of the user.
        :param status: The new status (0: deleted, 1: active).
        :return: True if the update was successful, False otherwise.
        """
        result = self.update(
            conditions=[
                {'column': 'id', 'value': key_id},
                {'column': 'user_id', 'value': user_id}
            ],
            data={'status': status}
        )
        return result > 0

    def delete_api_key(self, key_id: int, user_id: int) -> bool:
        """
        Soft delete an API key by setting its status to 0, ensuring it belongs to the specified user.
        
        :param key_id: The ID of the API key.
        :param user_id: The ID of the user.
        :return: True if the soft deletion was successful, False otherwise.
        """
        result = self.update(
            conditions=[
                {'column': 'id', 'value': key_id},
                {'column': 'user_id', 'value': user_id}
            ],
            data={'status': 0}  # 0: deleted
        )
        return result > 0

    def update_last_used_time(self, key_id: int) -> bool:
        """
        Update the last used time of an API key.
        
        :param key_id: The ID of the API key.
        :return: True if the update was successful, False otherwise.
        """
        result = self.update(
            conditions=[{'column': 'id', 'value': key_id}],
            data={'last_used_time': datetime.now()}
        )
        return result > 0

    def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return its information if valid.
        
        :param api_key: The API key to validate.
        :return: A dictionary containing the API key information if valid, None otherwise.
        """
        return self.select_one(
            columns=[
                'id', 'app_id', 'user_id', 'key', 'status', 
                'last_used_time', 'created_time', 'updated_time'
            ],
            conditions=[
                {'column': 'key', 'value': api_key},
                {'column': 'status', 'value': 1}  # Only active keys are valid
            ]
        )