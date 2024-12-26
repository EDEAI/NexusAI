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
    have_updated_time = False

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

    def get_tag_binding_by_count_id(self, tag_id: int) -> int:
        '''
        Get the count of bindings for a specific tag.
        '''
        result = self.select_one(
            aggregates={"id": "count"},
            conditions=[{"column": "tag_id", "value": tag_id}]
        )
        return result['count_id'] if result else 0

    def batch_update_bindings(self, app_ids: List[int], tag_ids: List[int] = None) -> bool:
        """
        Update tag bindings for multiple apps.
        If tag_ids is None, remove all bindings for the given apps.

        Args:
            app_ids (List[int]): List of app IDs
            tag_ids (List[int], optional): List of tag IDs to bind. Defaults to None.

        Returns:
            bool: True if operation successful
        """
        try:
            # Get existing bindings
            existing_bindings = self.select(
                columns=["tag_id", "app_id"],
                conditions=[{"column": "app_id", "op": "in", "value": app_ids}]
            )
            
            existing_map = {binding['app_id']: set() for binding in existing_bindings}
            for binding in existing_bindings:
                existing_map[binding['app_id']].add(binding['tag_id'])

            for app_id in app_ids:
                existing_tag_ids = existing_map.get(app_id, set())
                
                if not tag_ids:
                    # Remove all bindings if tag_ids is empty
                    self.delete([{"column": "app_id", "value": app_id}])
                else:
                    # Calculate differences
                    tags_to_add = set(tag_ids) - existing_tag_ids
                    tags_to_remove = existing_tag_ids - set(tag_ids)

                    # Remove old bindings
                    if tags_to_remove:
                        self.delete([
                            {"column": "tag_id", "op": "in", "value": list(tags_to_remove)},
                            {"column": "app_id", "value": app_id}
                        ])

                    # Add new bindings
                    for tag_id in tags_to_add:
                        self.insert({
                            'tag_id': tag_id,
                            'app_id': app_id
                        })
            return True
        except Exception:
            return False