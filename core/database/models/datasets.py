from sqlalchemy.sql import text
from typing import Any, Dict, List
from core.database import MySQL
import math

from languages import get_language_content


class Datasets(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "datasets"
    """
    Indicates whether the `datasets` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_dataset_id(
        self,
        app_id: int,
        user_id: int = 0,
        language_key: str = 'api_vector_available_dataset',
        check_is_reindexing: bool = False
    ) -> int:
        """
        Retrieves the dataset ID associated with the given app ID.

        :param app_id: The ID of the app.
        :return: The dataset ID associated with the given app ID.
        """
        conditions = [
            {'column': 'app_id', 'value': app_id},
            {'column': 'status', 'op': '<', 'value': 3},
        ]

        if user_id > 0:
            conditions.append({'column': 'user_id', 'value': user_id})


        dataset = self.select_one(
            columns=['id', 'collection_name'],
            conditions=conditions,
        )
        assert dataset, get_language_content(language_key)
        if check_is_reindexing:
            assert dataset['collection_name'] != 'reindexing', get_language_content('api_vector_indexing')
        return dataset['id']

    def get_dataset_by_id(self, dataset_id: int, check_is_reindexing: bool = False) -> Dict[str, Any]:
        """
        Retrieves the dataset information for the given dataset ID.

        :param dataset_id: The ID of the dataset.
        :return: A dictionary containing the dataset information.
        """
        dataset = self.select_one(
            columns=[
                'id',
                'app_id',
                'process_rule_id',
                'collection_name',
                'embedding_model_config_id',
                'retriever_config'
            ],
            conditions=[
                {'column': 'id', 'value': dataset_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ]
        )
        assert dataset, get_language_content('api_vector_available_dataset')
        if check_is_reindexing:
            assert dataset['collection_name'] != 'reindexing', get_language_content('api_vector_indexing')
        return dataset

    def get_dataset_find(self, dataset_id: int, user_id: int, team_id: int) -> Dict[str, Any]:
        """
        Retrieves the dataset with the given ID, user ID, and team ID.

        :param dataset_id: The ID of the dataset.
        :param user_id: The ID of the user.
        :param team_id: The ID of the team.
        :return: The dataset with the given ID, user ID, and team ID.
        """
        datasets = self.select(
            columns=[
                'id'
            ],
            conditions=[
                {'column': 'id', 'value': dataset_id},
                {'column': 'user_id', 'value': user_id},
                {'column': 'team_id', 'value': team_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ],
            limit=1
        )
        assert datasets, get_language_content('api_vector_auth')
        return datasets[0]

    def get_dataset_is_public(self, dataset_id: int, team_id: int) -> int:
        """
        Checks if the dataset is public.

        :param dataset_id: The ID of the dataset.
        :param team_id: The ID of the team.
        :return: 1 if the dataset is public, 0 if it is not.
        """
        apps = self.select_one(
            columns=['apps.is_public'],
            joins=[
                ['left', 'apps', 'datasets.app_id = apps.id']
            ],
            conditions=[
                {'column': 'datasets.id', 'value': dataset_id},
                {'column': 'datasets.team_id', 'value': team_id},
                {'column': 'datasets.status', 'value': 1},
                {'column': 'apps.team_id', 'value': team_id},
                {'column': 'apps.status', 'value': 1},
            ],
        )
        assert apps, get_language_content('api_vector_auth')
        return apps['is_public']

    def get_app_by_id(self, dataset_id: int) -> int:
        return self.select_one(
            columns=['apps.id'],
            joins=[
                ['left', 'apps', 'datasets.app_id = apps.id']
            ],
            conditions=[
                {'column': 'datasets.id', 'value': dataset_id},
            ],
        )['id']

    def get_dataset_list(self, team_id: int, user_id: int, is_individual: int, temporary_chatroom_id: int = 0) -> List[Dict[str, Any]]:
        """
        Returns a list of datasets that the user has access to.

        :param team_id: The ID of the team.
        :param user_id: The ID of the user.
        :param is_individual: int, 1 personage 2 Team visible and individual
        :param temporary_chatroom_id: int, temporary chatroom id, default is 0
        :return: A list of datasets.
        """
        where = f"(B.is_public = 1 OR (B.is_public = 0 AND B.user_id = {user_id}))"
        if is_individual == 1:
            where = f"B.user_id = {user_id}"

        sql = f"""
                    SELECT A.id as dataset_id,B.id as app_id,B.name FROM `datasets` AS A
                    LEFT JOIN `apps` AS B ON A.app_id = B.id
                    WHERE A.team_id = {team_id} AND A.status < 3 AND {where}
                    AND A.temporary_chatroom_id = {temporary_chatroom_id}  
                """
        return self.execute_query(sql).fetchall()

    def get_dataset_detail(self, dataset_id: int) -> Dict[str, Any]:
        """
        Returns a dataset detail.

        :param dataset_id: The ID of the dataset.
        :return: A dictionary containing the dataset information.
        """
        return self.select_one(
            columns=['datasets.id', 'apps.name', 'apps.description', 'apps.is_public', 'models.mode', 'users.nickname'],
            joins=[
                ['left', 'apps', 'datasets.app_id = apps.id'],
                ['left', 'model_configurations', 'datasets.embedding_model_config_id = model_configurations.id'],
                ['left', 'models', 'model_configurations.model_id = models.id'],
                ['left', 'users', 'datasets.user_id = users.id']
            ],
            conditions=[
                {'column': 'datasets.id', 'value': dataset_id},
                {'column': 'apps.mode', 'value': 3},
                {'column': 'datasets.status', 'op': '<', 'value': 3},
                {'column': 'apps.status', 'op': '<', 'value': 3},
                {'column': 'apps.status', 'op': '<', 'value': 3},
                {'column': 'model_configurations.status', 'op': '<', 'value': 3},
                {'column': 'models.status', 'op': '<', 'value': 3},
                {'column': 'users.status', 'op': '<', 'value': 3},
            ],
        )

    def get_dataset_is_indexing_status(self, dataset_id: int) -> Dict[str, Any]:
        """
        Returns status of the dataset.

        :param dataset_id: The ID of the dataset.
        :return: A dictionary containing the dataset information.
        """
        return self.select_one(
            columns=['document_segments.id'],
            joins=[
                ['left', 'documents', 'datasets.id = documents.dataset_id'],
                ['left', 'document_segments', 'documents.id = document_segments.document_id'],
            ],
            conditions=[
                {'column': 'datasets.id', 'value': dataset_id},
                {'column': 'datasets.status', 'op': '<', 'value': 3},
                {'column': 'documents.status', 'op': '<', 'value': 3},
                {'column': 'document_segments.status', 'op': '<', 'value': 3},
                {'column': 'document_segments.indexing_status', 'value': 1},
            ]
        )