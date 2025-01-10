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

    def initialize_execution_record(self, app_run_id: int, ai_tool_type: int, run_type: int = 1, loop_id: int = 0, loop_limit: int = 0, loop_count: int = 0, inputs: Dict[str, Any] = None, correct_prompt: Dict[str, Any] = None) -> int:
        """
        Initializes an execution record with the given parameters.
        
        Args:
            app_run_id (int): The ID of the app run.
            ai_tool_type (int): AI tool type 0: Regular APP (not an AI tool) 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator.
            run_type (int): The type of the current operation. 1: First generation 2: Regeneration 3: AI correction 4: Batch generation.
            loop_id (int): The number of iterations required for looping, represented as a positive integer indicating how many times the execution process should iterate.
            loop_limit (int): The maximum number of iterations allowed for looping.
            loop_count (int): The number of iterations required for looping.
            inputs (Dict[str, Any]): The inputs for the execution record.
            correct_prompt (Dict[str, Any]): The correct prompt for the execution record.
        
        Returns:
            int: The ID of the newly created record.
        """
        # loop_count = max(loop_count - 1, 0)
        record = {
            'app_run_id': app_run_id,
            'status': 1,
            'ai_tool_type': ai_tool_type,
            'run_type': run_type,
            'loop_id': loop_id,
            'loop_limit': loop_limit,
            'loop_count': loop_count
        }
        if inputs is not None:
            record['inputs'] = inputs
        if correct_prompt is not None:
            record['correct_prompt'] = correct_prompt

        return self.insert(record)

    def initialize_correction_record(self, app_run_id: int, ai_tool_type: int, loop_count: int = 0, correct_prompt: Dict[str, Any] = None) -> int:
        """
        Initializes an AI correction record with the given parameters.
        
        Args:
            app_run_id (int): The ID of the app run.
            ai_tool_type (int): AI tool type 0: Regular APP (not an AI tool) 1: Agent generator 2: Skill generator 3: Round Table meeting summary generator 4: Round Table app target data generator.
            loop_count (int): The number of iterations required for looping.
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
        return self.initialize_execution_record(app_run_id, ai_tool_type, 3, loop_count, correct_prompt=correct_prompt)

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
                'run_type',
                # 'app_runs.ai_tool_type',
                'ai_tool_type',
                'loop_id',
                'loop_count',
                'loop_limit',
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
            ],
            order_by='id ASC'
        )

    def get_history_record(self, app_run_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the last two execution records for a given app run.
        
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

    def get_search_record(self, app_run_id: int, ai_tool_type: int, run_type: int, loop_id: int) -> Dict[str, Any]:
        """
        Retrieves the search records based on the provided parameters.

        Args:
            app_run_id (int): The ID of the application run.
            ai_tool_type (int): The type of AI tool used.
            run_type (int): The type of run.
            loop_id (int): The ID of the loop.

        Returns:
            Dict[str, A dictionary representing.
        """
        status = self.select_one(
            columns=['status'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "ai_tool_type", "value": ai_tool_type},
                {"column": "run_type", "value": run_type},
                {"column": "loop_id", "value": loop_id},
                {"column": "loop_count", "op": ">", "value": 0},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        return status

    def inputs_append_history_outputs(self, app_run_id: int, loop_id: int = 0, agent_supplement: str = None) -> dict:
        """
        Append outputs values from all records and prepare prompts for batch generation
        
        Args:
            app_run_id (int): The ID of the app run
            loop_id (int): The ID of the loop iteration (default: 0)
            agent_supplement (str): Additional requirements for agent generation
            
        Returns:
            dict: Input dictionary containing system and user prompts
        """
        from languages import get_language_content
        from core.llm.prompt import Prompt

        # Get user ID from app_runs
        userinfo = self.select_one(
            joins=[
                ['left', 'app_runs', 'ai_tool_llm_records.app_run_id = app_runs.id']
            ],
            columns=['app_runs.user_id'],
            conditions=[
                {"column": "ai_tool_llm_records.app_run_id", "value": app_run_id},
            ]
        )

        # Get all records for current batch
        batch_records = self.select(
            columns=['id', 'inputs', 'outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "loop_id", "value": loop_id},
            ],
            order_by='id ASC'
        )

        # Extract outputs values into a list
        outputs_list = []
        for record in batch_records:
            if record.get('outputs') and isinstance(record['outputs'], dict):
                output_value = record['outputs'].get('value')
                if output_value:
                    outputs_list.append(output_value)

        # Prepare prompts based on whether this is a continuation or new batch
        if batch_records:
            # Get base user prompt from first record of current batch
            base_user_prompt = ""
            try:
                inputs = batch_records[0].get('inputs', {})
                if isinstance(inputs, dict):
                    user_dict = inputs.get('user', {})
                    if isinstance(user_dict, dict):
                        base_user_prompt = user_dict.get('value', '')
            except Exception:
                pass

            # Format user prompt with history
            user_prompt = get_language_content('agent_batch_generate_history_user', userinfo['user_id'], False)
            user_prompt = user_prompt.format(
                history_prompt=base_user_prompt,
                history_agents=outputs_list
            )
        else:
            # Get first record of original generation
            first_record = self.select_one(
                columns=['inputs'],
                conditions=[
                    {"column": "app_run_id", "value": app_run_id},
                    {"column": "loop_id", "value": 0}
                ],
                order_by='id ASC'
            )

            # Get base user prompt
            base_user_prompt = ""
            if first_record and isinstance(first_record.get('inputs'), dict):
                user_dict = first_record['inputs'].get('user', {})
                if isinstance(user_dict, dict):
                    base_user_prompt = user_dict.get('value', '')

            # Get latest agent data
            latest_record = self.select_one(
                columns=['outputs'],
                conditions=[
                    {"column": "app_run_id", "value": app_run_id},
                    {"column": "loop_id", "value": 0}
                ],
                order_by='id DESC'
            )

            # Format user prompt for new batch
            user_prompt = get_language_content('agent_batch_generate_user', userinfo['user_id'], False)
            user_prompt = user_prompt.format(
                first_user_prompt=base_user_prompt,
                agent_supplement=agent_supplement,
                agent_data=latest_record['outputs'] if latest_record else {},
                history_agents=outputs_list
            )

        # Prepare system prompt
        system_prompt = get_language_content('agent_batch_generate_system', userinfo['user_id'])
        # system_prompt = system_prompt.format(
        #     append_prompt=get_language_content('agent_batch_generate_system', userinfo['user_id'])
        # )

        # Return formatted prompts
        return Prompt(system=system_prompt, user=user_prompt).to_dict()


    def get_record_loop_count(self, app_run_id: int, loop_id: int) -> int:
        result = self.select(
            aggregates={"loop_count": "sum"},
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "loop_id", "value": loop_id}
            ]
        )
        return result[0]["sum_loop_count"] if result else 0
       
