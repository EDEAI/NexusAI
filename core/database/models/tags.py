from typing import Any, Dict, List
from core.database import MySQL


class Tags(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "tags"
    """
    Indicates whether the `tags` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_tag_by_id(self, tag_id: int, user_id: int, team_id: int) -> Dict[str, Any]:
        """
        Retrieves a tag by its ID.

        Args:
            tag_id (int): The ID of the tag to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the tag information.
        """
        tag = self.select_one(
            columns=[
                'id',
                'team_id',
                'user_id',
                'mode',
                'name',
                'status'
            ],
            conditions=[
                {"column": "id", "value": tag_id},
                {"column": "user_id", "value": user_id},
                {"column": "team_id", "value": team_id},
                {"column": "status", "value": 1}
            ]
        )
        return tag
    def get_tag_list(self,user_id: int,team_id: int,mode: int = None)->List[Dict[str,Any]]:
        '''
        Get a list of tags.
        
        Parameters: 
        - user_id: int, user id
        - mode: int, mode of the tags
        - team_id: int, team id

        Returns:
        - List[Dict[str, Any]]: A list of dictionaries containing tag information.
        '''
        if mode:
            conditions = [
                {"column": "team_id", "value": team_id},
                {"column": "user_id", "value": user_id},
                {"column": "mode", "value": mode},
                {"column": "status", "value": 1}
            ]
        else:
            conditions = [
                {"column": "team_id", "value": team_id},
                {"column": "user_id", "value": user_id},
                {"column": "status", "value": 1}
            ]
        return self.select(columns="*", conditions=conditions, order_by="created_time DESC")
    def insert_tag(self,team_id: int, user_id: int, mode: int, name: str) -> int:
        """
        Insert a new tag.

        Args:
            team_id (int): The ID of the team the tag belongs to.
            user_id (int): The ID of the user creating the tag.
            mode (int): The mode of the tag.
            name (str): The name of the tag.

        Returns:
            int: The ID of the newly created tag.
        """
        tag_id = self.insert({
            'team_id': team_id,
            'user_id': user_id,
            'mode': mode,
            'name': name,
        })
        return tag_id
    def update_tag(self,tag_id: int, name: str,team_id: int,user_id: int) -> bool:
        """
        Update an existing tag.

        Args:
            tag_id (int): The ID of the tag to update.
            name (str): The new name of the tag.
            team_id (int): The ID of the team the tag belongs to.
            user_id (int): The ID of the user updating the

        Returns:
            bool: True if the tag was successfully updated, False otherwise.
        """
        return self.update(
            [
            {"column": "id", "value": tag_id},
            {"column": "team_id", "value": team_id},
            {"column": "user_id", "value": user_id}
            ],
            {
            'name': name
            }
        )