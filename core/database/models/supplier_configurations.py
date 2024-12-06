from typing import Any, Dict, List
from core.database import MySQL

class SupplierConfigurations(MySQL):
    """
    Extends MySQL to manage operations on the supplier_configurations table.
    """
    
    table_name: str = "supplier_configurations"
    """
    Indicates whether the supplier_configurations table has an update_time column that tracks when a record was last updated.
    """
    have_updated_time = True
    def get_supplier_config_id(self, supplier_id: int,team_id: int) -> Dict:
        """
        Retrieves a supplier's configuration based on their ID.
        
        Args:
        - supplier_id (int): The ID of the supplier to retrieve configuration for.
        
        Returns:
        - Dict: A dictionary containing the supplier's configuration.
        """
        supplier_config = self.select_one(columns="*", conditions=[{'column': 'supplier_id', 'value': supplier_id},{'column': 'team_id', 'value': team_id}])
        return supplier_config
