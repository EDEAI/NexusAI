from typing import Any, Dict, List
from core.database import MySQL
from core.database.models import Users
from core.database.models.app_node_executions import AppNodeExecutions
import math


class AppNodeUserRelation(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "app_node_user_relation"
    have_updated_time = True

    def create_data(self, app_run_id, node_list):
        users = Users()
        
        all_user_ids = list({user_id for user_ids in node_list.values() for user_id in user_ids})
        user_data_list = users.select(
            columns=['id', 'team_id'],
            conditions=[
                {"column": "id", "op": "in", "value": all_user_ids},
                {"column": "status", "value": 1}
            ]
        )

        user_data_dict = {user_data['id']: user_data for user_data in user_data_list}
        
        if len(user_data_dict) != len(all_user_ids):
            missing_users = set(all_user_ids) - set(user_data_dict.keys())
            raise ValueError(f'Users not exist: {missing_users}')
        
        for node_id, user_id_list in node_list.items():
            for user_id in user_id_list:
                self.insert({
                    'app_run_id': app_run_id,
                    'node_id': node_id,
                    'team_id': user_data_dict[user_id]['team_id'],
                    'user_id': user_id,
                })
                
    def get_node_user_ids(self, app_run_id, node_id):
        """
        Get the user IDs for a given node ID.

        :param app_run_id: The ID of the app run.
        :param node_id: The ID of the node.
        :return: A list of user IDs.
        """
        result = self.select(
            columns=['user_id'],
            conditions=[
                {'column': 'app_run_id', 'value': app_run_id},
                {'column': 'node_id', 'value': node_id}
            ]
        )
        return [user['user_id'] for user in result] if result else []
    
    
    def add_node_user_relation(self, app_run_id: int, node_id: int, team_id: int, user_id: int):
        """
        Add a user to the node user relation table if not already present.

        :param app_run_id: The ID of the app run.
        :param node_id: The ID of the node.
        :param team_id: The ID of the team.
        :param user_id: The ID of the user.
        :return: None
        """
        existing_relation = self.select(
            columns=['id'],
            conditions=[
                {'column': 'app_run_id', 'value': app_run_id},
                {'column': 'node_id', 'value': node_id},
                {'column': 'team_id', 'value': team_id},
                {'column': 'user_id', 'value': user_id}
            ]
        )
        
        if existing_relation:
            return
        
        self.insert({
            'app_run_id': app_run_id,
            'node_id': node_id,
            'team_id': team_id,
            'user_id': user_id,
        })