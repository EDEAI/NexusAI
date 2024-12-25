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