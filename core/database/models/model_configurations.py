from typing import Any, Dict, List
from core.database import MySQL
from languages import get_language_content


class ModelConfigurations(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name: str = "model_configurations"
    """
    Indicates whether the `model_configurations` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_config_by_team_id_and_model_id(self, team_id: int, model_id: int):
        """
        Gets the model configuration details by team ID and model configuration ID.

        :param team_id: The ID of the team.
        :param model_id: The ID of the model.
        :return: A dictionary containing the model details.
        """
        config = self.select_one(
            columns=[
                'id'
            ],
            conditions=[
                {'column': 'team_id', 'value': team_id},
                {'column': 'model_id', 'value': model_id},
                {'column': 'status', 'value': 1},
            ]
        )
        assert config, get_language_content('api_vector_available_dataset')
        return config

    def get_models_id(self, embedding_model_config_id: int, team_id: int) -> int:
        return self.select_one(
            columns=[
                'model_id'
            ],
            conditions=[
                {'column': 'team_id', 'value': team_id},
                {'column': 'id', 'value': embedding_model_config_id},
                {'column': 'status', 'op': '<', 'value': 3},
            ]
        )['model_id']

    def get_models_default_used_by_id(self, _type: int, team_id: int) -> int:
        model_id = self.select_one(
            columns=["model_configurations.id AS m_config_id", "model_configurations.model_id AS m_id",
                     "models.name AS m_name", "models.supplier_id", "suppliers.name AS supplier_name"],
            joins=[
                ["left", "models", "model_configurations.model_id = models.id"],
                ["left", "suppliers", "models.supplier_id = suppliers.id"]
            ],
            conditions=[
                {"column": "model_configurations.team_id", "value": team_id},
                {"column": "model_configurations.status", "value": 1},
                {"column": "models.type", "value": _type},
                {"column": "models.status", "value": 1},
                {"column": "suppliers.status", "value": 1}
            ]
        )
        if model_id:
            return model_id['m_config_id']
        else:
            return None