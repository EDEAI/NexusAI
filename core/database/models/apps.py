from typing import Any, Dict
from core.database import MySQL
import math
from core.database.models.app_workflow_relation import AppWorkflowRelations
from core.database.models.tag_bindings import TagBindings
from core.helper import generate_api_token
from languages import get_language_content


class Apps(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name: str = "apps"
    """
    Indicates whether the `apps` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_app_by_id(self, app_id: int) -> Dict[str, Any]:
        app = self.select_one(
            columns=[
                'id',
                'team_id',
                'name',
                'description',
                'is_public',
                'execution_times',
                'icon'
            ],
            conditions=[
                {'column': 'id', 'value': app_id},
                {'column': 'status', 'value': 1},
            ]
        )
        assert app, 'No available app!'
        return app

    def get_app_by_is_public(self, app_id: int, team_id: int) -> Dict[str, Any]:
        """
        Retrieves the dataset with the given ID, user ID, and team ID.

        :param app_id: The ID of the app.
        :param team_id: The ID of the team.
        :return: A dictionary containing the dataset information.
        """
        datasets = self.select(
            columns=[
                'is_public'
            ],
            conditions=[
                {'column': 'id', 'value': app_id},
                {'column': 'team_id', 'value': team_id},
                {'column': 'mode', 'value': 3},
                {"column": "status", "op": "in", "value": [1, 2]},
            ],
            limit=1
        )
        assert datasets, get_language_content('api_vector_available_apps')
        return datasets[0]['is_public']

    def get_app_list(self, page, page_size, search_type, apps_name, apps_mode, user_id, team_id, tag_ids):
        """
        Obtain apps list data based on parameters
        :param page: Page number.
        :param page_size: Quantity per page.
        :param uid: User ID.
        :param team_id: Team ID.
        :param search_type: Agent search type 1: my agent 2: team agent .
        :return: A dictionary representing the app list record.
        """
        if search_type == 1:
            conditions = [
                {"column": "apps.user_id", "value": user_id},
                {"column": "apps.status", "op": "in", "value": [1, 2]},
            ]
        else:
            conditions = [
                {"column": "apps.team_id", "value": team_id},
                {"column": "apps.is_public", "value": 1},
                {"column": "apps.user_id", "op": "!=", "value": user_id},
                {"column": "apps.publish_status", "value": 1},
                {"column": "apps.status", "value": 1},
            ]
        if apps_name:
            conditions.append({"column": "apps.name", "op": "like", "value": "%" + apps_name + "%"})

        apps_mode_list = apps_mode.split(',')
        if len(apps_mode_list) == 1:
            if int(apps_mode) not in [1, 2, 3, 4]:
                conditions.append({"column": "apps.mode", "op": "in", "value": [1, 2, 4]})
            else:
                conditions.append({"column": "apps.mode", "value": int(apps_mode)})
        else:
            conditions.append({"column": "apps.mode", "op": "in", "value": [int(i) for i in apps_mode_list]})
        if tag_ids != '0' and tag_ids:
            app_ids = TagBindings().get_tag_apps_by_tag_id(tag_ids,user_id, apps_mode)
            conditions.append({"column": "apps.id", "op": "in", "value": app_ids})
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions,
        )['count_id']

        all_app = self.select(
            columns=[
                'apps.id AS app_id', 'apps.name', 'apps.description', 'apps.mode', 'apps.icon', 'apps.icon_background',
                'apps.execution_times', 'apps.publish_status'
            ],
            conditions=conditions,
            order_by="apps.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        workflow_app_ids = []
        other_app_ids = []
        for item in all_app:
            tag_datas = TagBindings().get_tags_by_app_id(item['app_id'],user_id)
            item['tags'] = tag_datas
            if item['mode'] == 2:  # Assuming mode 2 represents workflow apps
                workflow_app_ids.append(item['app_id'])
            else:
                other_app_ids.append(item['app_id'])

        # Query Association Table
        info_workflow = AppWorkflowRelations().select(
            columns=[
                'apps.id AS apps_id', 'app_id', 'apps.name', 'apps.description', 'apps.mode', 'apps.icon',
                'apps.icon_background'
            ],
            joins=[
                ["left", "apps", "app_workflow_relation.workflow_app_id = apps.id"],
            ],
            conditions=[
                {"column": "app_workflow_relation.app_id", "op": "in", "value": other_app_ids},
                {"column": "apps.status", "op": "in", "value": [1, 2]},
            ]
        )
        workflow_dict = {}
        other_dict = {}
        for item in all_app:
            if item['mode'] == 2:
                workflow_dict[item['app_id']] = []
            else:
                other_dict[item['app_id']] = []

        for info_item in info_workflow:
            if info_item['app_id'] in other_dict:
                other_dict[info_item['app_id']].append(info_item)

        info_app = self.select(
            columns=[
                'apps.id AS apps_id', 'apps.name', 'app_workflow_relation.workflow_app_id', 'apps.description',
                'apps.mode', 'apps.icon',
                'apps.icon_background'
            ],
            joins=[
                ["left", "app_workflow_relation", "apps.id = app_workflow_relation.app_id"],
            ],
            conditions=[
                {"column": "app_workflow_relation.workflow_app_id", "op": "in", "value": workflow_app_ids},
                {"column": "apps.status", "op": "in", "value": [1, 2]},
            ]
        )

        for app_item in info_app:
            if app_item['workflow_app_id'] in workflow_dict:
                workflow_dict[app_item['workflow_app_id']].append(app_item)

        for data_item in all_app:
            if data_item['mode'] == 2:
                data_item['list'] = workflow_dict[data_item['app_id']]
            else:
                data_item['list'] = other_dict[data_item['app_id']]

        return {
            "list": all_app,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size,
        }

    def increment_execution_times(self, app_id: int) -> bool:
        """
        Increments the execution_times field by 1 for the specified app.

        :param app_id: The ID of the app to update.
        :return: True if the update affected one or more rows, False otherwise.
        """
        sql = f"UPDATE {self.table_name} SET execution_times = execution_times + 1, updated_time = NOW() WHERE id = {app_id}"
        result = self.execute_query(sql)
        return result.rowcount > 0

    def get_app_find(self, app_id: int, user_id: int, team_id: int) -> Dict[str, any]:
        """
        Returns the app information for the specified app ID, user ID, and team ID.

        :param app_id: The ID of the app.
        :param user_id: The ID of the user.
        :param team_id: The ID of the team.
        :return: A dictionary containing the app information.
        """
        apps = self.select_one(
            columns='*',
            conditions=[
                {'column': 'id', 'value': app_id},
                {'column': 'team_id', 'value': team_id},
                {'column': 'user_id', 'value': user_id},
                {"column": "status", "op": "in", "value": [1, 2]},
            ],
        )
        assert apps, get_language_content('api_vector_available_apps')
        return apps

    def update_publish_status(self, app_id: int) -> bool:
        """
        Updates the publish_status field for the specified app.

        :param app_id: The ID of the app to update.
        :param publish_status: The new publish status value.
        :return: True if the update affected one or more rows, False otherwise.
        """
        api_token = generate_api_token()
        sql = f"UPDATE {self.table_name} SET publish_status = 1 WHERE id = {app_id}"
        result = self.execute_query(sql)
        sql = f"UPDATE {self.table_name} SET api_token = '{api_token}' WHERE id = {app_id} AND api_token IS NULL"
        result = self.execute_query(sql)
        return result.rowcount > 0

    def get_app_by_id_search(self, app_id: int) -> Dict[str, Any]:
        app = self.select_one(
            columns=[
                'id',
                'team_id',
                'mode',
                'is_public',
                'user_id'
            ],
            conditions=[
                {'column': 'id', 'value': app_id},
                {'column': 'status', 'value': 1},
                {'column': 'mode', 'op': 'in', 'value': [1, 2]},
                {'column': 'publish_status', 'value': 1}
            ]
        )
        return app
