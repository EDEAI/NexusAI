from typing import Any, Dict, List
from core.database import MySQL

class DatasetProcessRules(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "dataset_process_rules"
    """
    Indicates whether the `dataset_process_rules` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    
    
    def get_automatic_process_rule(self) -> Dict[str, Any]:
        process_rule = self.select_one(
            columns=['id'],
            conditions=[
                {'column': 'mode', 'value': 1},
                {'column': 'status', 'value': 1}
            ]
        )
        assert process_rule, 'No available dataset process rule!'
        return process_rule
    
    def get_process_rule_by_id(self, process_rule_id: int) -> Dict[str, Any]:
        """
        Retrieves the process rule configuration for a given process rule ID.

        :param process_rule_id: The process rule ID.
        :return: The process rule configuration.
        """
        process_rule = self.select_one(
            columns=['config'],
            conditions=[
                {'column': 'id', 'value': process_rule_id},
                {'column': 'status', 'value': 1}
            ]
        )
        return process_rule
    