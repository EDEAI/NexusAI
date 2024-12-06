from typing import Any, Dict, List, Literal, Tuple
from core.database import MySQL
from languages import get_language_content


class Models(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "models"
    """
    Indicates whether the `models` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    
    
    def get_model_by_type_and_indexing_mode(
        self,
        model_type: int,
        indexing_mode: Literal[1, 2]
    ) -> Dict[str, Any]:
        model = self.select_one(
            columns=[
                'models.id',
                'models.name',
                'suppliers.name AS supplier_name'
            ],
            joins=[
                ['inner', 'suppliers', 'models.supplier_id = suppliers.id']
            ],
            conditions=[
                {'column': 'models.type', 'value': model_type},
                {'column': 'models.indexing_mode', 'value': indexing_mode},
                {'column': 'models.status', 'value': 1},
                {'column': 'suppliers.status', 'value': 1},
            ]
        )
        assert model, 'No available model!'
        return model
        
    def get_model_by_config_id(self, model_config_id: int) -> Dict[str, Any]:
        """
        Gets the model details by model configuration ID.
        
        :param model_config_id: The ID of the model configuration.
        :return: A dictionary containing the model details.
        """
        model = self.select_one(
            columns=[
                'models.id AS model_id',
                'models.name AS model_name',
                'models.type AS model_type',
                'models.mode AS model_mode',
                'suppliers.id AS supplier_id',
                'suppliers.name AS supplier_name',
                'supplier_configurations.config AS supplier_config',
                'model_configurations.config AS model_config'
            ],
            joins=[
                ['inner', 'suppliers', 'models.supplier_id = suppliers.id'],
                ['inner', 'supplier_configurations', 'suppliers.id = supplier_configurations.supplier_id'],
                ['inner', 'model_configurations', 'models.id = model_configurations.model_id']
            ],
            conditions=[
                {'column': 'model_configurations.id', 'value': model_config_id},
                {'column': 'models.status', 'value': 1},
                {'column': 'suppliers.status', 'value': 1},
                {'column': 'supplier_configurations.status', 'value': 1},
                {'column': 'model_configurations.status', 'value': 1}
            ]
        )
        assert model, get_language_content('api_vector_available_model')
        return model

    def get_model_config_llm_list(self) -> List:
        '''
        Find the list of associated config using the model of type llm
        and return model_configurations.id and models.name, sorted by model_configurations.default_used.
        '''
        models = self.select(
            columns=[
                'model_configurations.id AS model_config_id',
                'models.name AS model_name',
                'model_configurations.default_used AS model_default_used',
            ],
            joins=[
                ['inner', 'model_configurations', 'models.id = model_configurations.model_id']
            ],
            conditions=[
                {'column': 'models.type', 'value': 1},
            ],
            order_by='model_configurations.default_used DESC'
        )
        return models

    def get_model_information(self, model_ids: Tuple) -> list:
        """
        Get information about the specified models.

        :param model_ids: A tuple of model IDs.
        :return: A list of model information.
        """
        cmd_sql = f"""
            SELECT A.id,A.name,A.mode,B.name as suppliers_name FROM models AS A 
            LEFT JOIN suppliers AS B ON A.supplier_id = B.id
            WHERE A.id in {model_ids}
        """
        data = self.execute_query(cmd_sql).fetchall()
        return [{'id': item[0], 'name': item[1], 'mode': item[2], 'suppliers_name': item[3]} for item in data]
    
    def get_models_by_supplier_id(self, supplier_id: int) -> List:
        """
        Get models associated with a specific supplier ID.

        :param supplier_id: The ID of the supplier.
        :return: A list of models associated with the supplier.
        """
        models = self.select(
            columns="*",
            conditions=[{'column': 'supplier_id', 'value': supplier_id}]
        )
        return models
    
    def get_model_by_type(self, type_: int, team_id: int, indexing_mode: int = 0, uid: int = 0) -> Dict[str, Any]:
        """
        Get the model details by the type of the model configuration.
        Model type 1: text-generation 2: embeddings 3: reranking 4: speech2text 5: tts 6: text2img 7: moderation
        """
        conditions = [
            {'column': 'models.status', 'value': 1},
            {'column': 'suppliers.status', 'value': 1},
            {'column': 'supplier_configurations.status', 'value': 1},
            {'column': 'model_configurations.status', 'value': 1},
            {'column': 'model_configurations.default_used', 'value': 1},
            {'column': 'model_configurations.team_id', 'value': team_id},
            {'column': 'models.type', 'value': type_}
        ]
        if indexing_mode != 0:
            conditions.append({'column': 'models.mode', 'value': indexing_mode})

        model = self.select_one(
            columns=[
                'models.id AS model_id',
                'models.name AS model_name',
                'models.type AS model_type',
                'models.mode AS model_mode',
                'suppliers.id AS supplier_id',
                'suppliers.name AS supplier_name',
                'supplier_configurations.config AS supplier_config',
                'model_configurations.id AS model_config_id',
                'model_configurations.config AS model_config'
            ],
            joins=[
                ['inner', 'suppliers', 'models.supplier_id = suppliers.id'],
                ['inner', 'supplier_configurations', 'suppliers.id = supplier_configurations.supplier_id'],
                ['inner', 'model_configurations', 'models.id = model_configurations.model_id']
            ],
            conditions=conditions
        )
        assert model, get_language_content('api_vector_available_model', uid)
        return model
