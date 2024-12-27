from typing import Any, Dict, List
from core.database import MySQL


class AIToolLLMRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "ai_tool_llm_records"
    """
    Indicates whether the `ai_tool_llm_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    
    
    def get_history_record(self, app_run_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the last two node execution records for a given app run.
        
        Args:
            app_run_id (int): The ID of the app run.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing record data.
        """
        return self.select(
            columns=['correct_prompt', 'model_data', 'outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "status", "op": "in", "value": [2, 3]}
            ],
            order_by='id DESC',
            limit=2
        )