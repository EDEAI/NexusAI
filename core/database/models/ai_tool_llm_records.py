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
    
    
    def initialize_execution_record(self, app_run_id: int, inputs: Dict[str, Any] = None, correct_prompt: Dict[str, Any] = None) -> int:
        """
        Initializes an execution record with the given parameters.
        
        Args:
            app_run_id (int): The ID of the app run.
            inputs (Dict[str, Any]): The inputs for the execution record.
            correct_prompt (Dict[str, Any]): The correct prompt for the execution record.
        
        Returns:
            int: The ID of the newly created record.
        """
        record = {
            'app_run_id': app_run_id,
            'status': 1
        }
        if inputs is not None:
            record['inputs'] = inputs
        if correct_prompt is not None:
            record['correct_prompt'] = correct_prompt
        
        return self.insert(record)
    
    def initialize_correction_record(self, app_run_id: int, correct_prompt: Dict[str, Any] = None) -> int:
        """
        Initializes an AI correction record with the given parameters.
        
        Args:
            app_run_id (int): The ID of the app run.
            correct_prompt (Dict[str, Any]): The correct prompt for the correction record.
        
        Returns:
            int: The ID of the newly created correction record.
        
        Raises:
            ValueError: If no previous record with correct_output = 0 is found.
        """
        last_record = self.select_one(
            columns=['id'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "correct_output", "value": 0}
            ],
            order_by='id DESC',
            limit=1
        )
        if not last_record:
            raise ValueError("No previous record found.")
        
        self.update(
            conditions=[{"column": "id", "value": last_record['id']}],
            data={"correct_output": 1}
        )
        
        # Initialize the next correction record
        return self.initialize_execution_record(app_run_id, correct_prompt=correct_prompt)
    
    def get_pending_ai_tool_tasks(self) -> List[Dict[str, Any]]:
        """
        Queries pending AI tool tasks.
        
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing task data.
        """
        return self.select(
            columns=[
                'id',
                'app_run_id',
                'app_runs.ai_tool_type',
                'inputs',
                'correct_prompt',
                'outputs',
                'status',
                'elapsed_time',
                'prompt_tokens',
                'completion_tokens',
                'total_tokens',
                'created_time',
                'finished_time'
            ],
            joins=[
                ('inner', 'app_runs', 'ai_tool_llm_records.app_run_id = app_runs.id')
            ],
            conditions=[
                {"column": "app_runs.status", "value": 1},
                {"column": "status", "value": 1}
            ]
        )
    
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