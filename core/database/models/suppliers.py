from typing import Any, Dict, List
from core.database import MySQL

class Suppliers(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "suppliers"
    """
    Indicates whether the `suppliers` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_supplier_id(self, supplier_id: str) -> Dict:
        """
        Retrieves a supplier's information based on their name.
        
        Args:
        - supplier_name (str): The name of the supplier to retrieve.
        
        Returns:
        - Dict: A dictionary containing the supplier's information.
        """
        supplier = self.select_one(columns="*", conditions=[{'column': 'id', 'value': supplier_id}])
        return supplier


    def get_supplier_model_online_list(self, team_id: int) -> List:
        """
        Fetches the list of online suppliers along with their models, sorted by model_default_used with 1 first and 0 last.
        
        Returns:
        - List: A list of dictionaries containing information about online suppliers and their models.
        """
        columns = [
            'suppliers.id AS supplier_id',
            'suppliers.name AS supplier_name',
            'suppliers.mode AS supplier_mode',
            'suppliers.status AS supplier_status',
            'models.id AS model_id',
            'models.name AS model_name',
            'models.type AS model_type',
            'model_configurations.default_used AS model_default_used',
        ]
        joins = [
            ['inner', 'models', 'suppliers.id = models.supplier_id'],
            ['inner', 'model_configurations', 'models.id = model_configurations.model_id']
        ]
        conditions = [
            {'column': 'suppliers.status', 'value': 1},
            {'column': 'suppliers.mode', 'value': 1},
            {'column': 'models.status', 'value': 1},
            {'column': 'models.mode', 'value': 1},
            {'column': 'model_configurations.team_id', 'value': team_id},
            {'column': 'model_configurations.status', 'value': 1}
        ]
        order_by = 'model_configurations.default_used DESC'
        suppliers = self.select(columns=columns,joins=joins,conditions=conditions, order_by=order_by)

        return suppliers