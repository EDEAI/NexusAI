from typing import Any, Dict, List
from core.database import MySQL
from core.helper import get_tags_mode_by_app_modes


class TagBindings(MySQL):
    """
    A class that extends MySQL to manage operations on the tag_bindings table.
    """

    table_name = "tag_bindings"
    """
    Indicates whether the `tag_bindings` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_tag_apps_by_tag_id(self, tag_id: str, user_id: int, mode: str) -> list:
        """
        Retrieves a tag by its ID.

        Args:
            tag_id (int): The ID of the tag to retrieve.
            mode (str): The mode of the tag.

        Returns:
            list: A list of app IDs bound to the tag.
        """
        tag_ids = tag_id.split(',')
        _mode = get_tags_mode_by_app_modes(mode)
        # Get bound app IDs from tag_bindings table
        bound_apps = self.select(
            columns=['app_id'],
            joins=[
                ('inner', 'tags', 'tags.id = tag_bindings.tag_id')
            ],
            conditions=[
                {"column": "tags.id", "op": "in", "value": tag_ids},
                {"column": "tags.user_id", "value": user_id},
                {"column": "tags.mode", "op": "in", "value": _mode}
            ]
        )
        # Extract app IDs into a list
        app_list = [app['app_id'] for app in bound_apps]

        return app_list

    def get_tags_by_app_id(self, app_id: int, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all tags (with id and name) bound to a specific app.

        Args:
            app_id (int): The ID of the app to get tags for.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing tag information (id and name).
        """
        # Get tags bound to the app
        tags = self.select(
            columns=['tags.id', 'tags.name'],
            joins=[
                ('inner', 'tags', 'tags.id = tag_bindings.tag_id')
            ],
            conditions=[
                {"column": "tag_bindings.app_id", "value": app_id},
                {"column": "tags.user_id", "value": user_id},
                {"column": "tags.status", "value": 1}
            ]
        )

        return tags