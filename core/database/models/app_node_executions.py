from typing import Any, Dict, List, Tuple
from core.database import MySQL
import re


class AppNodeExecutions(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "app_node_executions"
    """
    Indicates whether the {table_name} table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    
    def get_node_successful_execution(self, app_run_id: int, node_id: str) -> Dict[str, Any]:
        """
        Retrieves the node execution record associated with the specified node ID.

        Args:
            app_run_id (int): The ID of the app run.
            node_id (str): The ID of the node.

        Returns:
            Dict[str, Any]: A dictionary representing the node execution record.
        """
        result = self.select_one(
            columns='*',
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "node_id", "value": node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ],
            order_by='id DESC'
        )
        return result
    
    def get_correct_llm_output_execution_ids(self, app_run_id: int, level: int, edge_id: str) -> Tuple[int, int]:
        """
        Retrieves the IDs of the node execution records associated with the specified node ID and correct output.
        
        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            edge_id (str): The ID of the edge.
        
        Returns:
            Tuple[int, int]: A tuple containing two integers:
                - The ID of the node execution record with correct output 0 and status 2.
                - The ID of the last node execution record with correct output 1.
        """
        correct_llm_output_execution_id = 0
        last_llm_execution_id = 0
        executions = self.select(
            columns=['id', 'correct_output', 'correct_prompt', 'status'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "edge_id", "value": edge_id}
            ],
            order_by='id DESC',
            limit=2
        )
        for execution in executions:
            if execution["correct_output"] == 0 and execution['correct_prompt'] and execution['status'] == 2:
                correct_llm_output_execution_id = execution['id']
            elif execution["correct_output"] == 1:
                last_llm_execution_id = execution['id']
        return correct_llm_output_execution_id, last_llm_execution_id
    
    def get_node_history(self, app_run_id: int, edge_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the history of node executions associated with the specified node ID.
        
        Args:
            app_run_id (int): The ID of the app run.
            edge_id (str): The ID of the edge.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a node execution record.
        """
        return self.select(
            columns=['correct_prompt', 'model_data', 'outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "edge_id", "value": edge_id},
                {"column": "status", "op": "in", "value": [2, 3]}
            ],
            order_by='id DESC',
            limit=2
        )
        
    def get_correct_llm_history(self, app_run_id: int, level: int, edge_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the history of node executions associated with the specified node ID and correct prompt.
        
        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            edge_id (str): The ID of the edge.
            
        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing a node execution record.
        """
        return self.select(
            columns=['correct_prompt', 'created_time'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "edge_id", "value": edge_id},
                {"column": "correct_prompt", "op": "is not null"}
            ]
        )

    def get_node_info(self, exec_id: int, uid: int, team_id: int) -> Dict[str, Any]:
        """
        Retrieves an agent record from the {table_name} table based on the specified exec ID.

        :param exec_id: An integer representing the exec ID.
        :return: A dictionary representing the node record.
        """
        node = self.select_one(
            columns=["id AS exec_id", "workflow_id", "user_id AS exec_user_id", "app_run_id", "type", "level", "child_level", "edge_id", 
                     "pre_node_id", "node_id", "node_type", "node_name", "node_graph", "inputs", "correct_prompt", "model_data", "task_id", "status", "error", "condition_id", "outputs", "output_type", 
                     "elapsed_time", "prompt_tokens", "completion_tokens", "total_tokens", "embedding_tokens", "reranking_tokens",
                     "created_time", "updated_time", "finished_time",
                     "apps.team_id", "apps.user_id", "app_runs.need_human_confirm", "app_runs.completed_steps", "app_runs.actual_completed_steps", "app_runs.status AS app_run_status", 
                     "app_runs.level AS app_run_level", "app_runs.completed_edges", "app_runs.context"],
            joins=[
                ["inner", "app_runs", "app_node_executions.app_run_id = app_runs.id"],
                ["inner", "apps", "app_runs.app_id = apps.id"]
            ],
            conditions=[
                {'column': 'id', 'value': exec_id}
            ]
        )
        if not node:
            return {"status": 2, "message": "node error"}
        if node["user_id"] != uid and node["team_id"] != team_id:
            return {"status": 2, "message": "The exec id is error"}

        return {"status": 1, "message": "success", "data": node}

    def get_human_node_exec(self, app_run_id: int, level: int, node_id: str) -> Dict[str, Any]:
        """
        Retrieves the human node execution record associated with the specified node ID.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            node_id (str): The ID of the node.

        Returns:
            Dict[str, Any]: A dictionary representing the human node execution record.
        """
        return self.select_one(
            columns=['id', 'node_graph', 'inputs', 'status'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "node_id", "value": node_id},
            ]
        )
        
    def has_human_confirm_node(self, app_run_id: int) -> bool:
        """
        Checks if there are any node execution records that require human confirmation for a given app run.

        Args:
            app_run_id (int): The ID of the app run.

        Returns:
            bool: True if there are node execution records that require human confirmation, False otherwise.
        """
        result = self.select_one(
            columns=['id'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "correct_output", "value": 0},
                {"column": "need_human_confirm", "value": 1}
            ]
        )
        return result is not None
    
    def is_corrected_data(self, exec_id: int) -> bool:
        """
        Checks if the record with the specified exec ID has been corrected (i.e., correct_output is 1).

        Args:
            exec_id (int): The primary key ID of the record.

        Returns:
            bool: True if the record has been corrected, False otherwise.
        """
        result = self.select_one(
            columns=['correct_output'],
            conditions=[
                {"column": "id", "value": exec_id}
            ]
        )
        return result is not None and result['correct_output'] == 1
    
    def get_all_task_execution_results(self, app_run_id: int, level: int, pre_node_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the list of task execution results.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            pre_node_id (str): The ID of the previous node.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing the task execution results.
        """
        results = self.select(
            columns=['id', 'child_level', 'node_id', 'task_id', 'condition_id', 'outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "pre_node_id", "value": pre_node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ]
        )
        return results
    
    def get_first_recursive_task_execution_id(self, app_run_id: int, level: int, node_id: str) -> int:
        """
        Retrieves the ID of the first execution record for a recursive task based on the specified parameters.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            node_id (str): The ID of the node.

        Returns:
            int: The ID of the first execution record.
        """
        first_execution = self.select_one(
            columns=['id'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "node_id", "value": node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3},
            ],
            order_by='id ASC'
        )
        return first_execution['id'] if first_execution else None
    
    def get_recursive_task_condition(self, app_run_id: int, level: int, node_id: str) -> Dict[str, Any]:
        """
        Retrieves the condition for executing a recursive task based on the specified parameters.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            node_id (str): The ID of the node.

        Returns:
            Dict[str, Any]: A dictionary containing the task condition.
        """
        current_execution = self.select_one(
            columns=['id', 'child_level', 'task_id', 'condition_id', 'outputs'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "node_id", "value": node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3},
            ],
            order_by='id DESC'
        )
        
        if not current_execution:
            return {"status": "assign_task", "child_level": 0}
        
        child_execution = self.select_one(
            columns=['id', 'child_level'],
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "pre_node_id", "value": node_id},
                {"column": "id", "op": ">", "value": current_execution['id']},
                {"column": "task_id", "op": "is not null"},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3},
            ],
            order_by='id ASC'
        )
        
        if child_execution:
            return {"status": "assign_task", "child_level": child_execution['child_level'] if child_execution['child_level'] > 0 else 1}
        
        return {
            "status": "execute_task", 
            "child_level": current_execution['child_level'],
            "task_id": current_execution['task_id'], 
            "executor_id": current_execution['condition_id'], 
            "parent_output": current_execution['outputs'],
            "first_execution_id": self.get_first_recursive_task_execution_id(app_run_id, level, node_id)
        }
        
    def get_task_total_data(self, app_run_id: int, level: int, node_id: str) -> Dict[str, int]:
        """
        Retrieves the total data for all task execution data.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            node_id (str): The ID of the node.

        Returns:
            Dict[str, int]: A dictionary containing the total elapsed time for all task execution data.
        """
        task_assignments_total = self.select_one(
            aggregates={'elapsed_time': 'sum'},
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "node_id", "value": node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ]
        )

        task_executions_total = self.select_one(
            aggregates={'elapsed_time': 'sum'},
            conditions=[
                {"column": "app_run_id", "value": app_run_id},
                {"column": "level", "value": level},
                {"column": "pre_node_id", "value": node_id},
                {"column": "task_id", "op": "is not null"},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ]
        )

        task_assignments_total_time = task_assignments_total['sum_elapsed_time'] if task_assignments_total else 0
        task_executions_total_time = task_executions_total['sum_elapsed_time'] if task_executions_total else 0
        total_elapsed_time = task_assignments_total_time + task_executions_total_time

        return {"total_elapsed_time": total_elapsed_time}

    def get_last_task_assignment(self, app_run_id: int, level: int, node_id: str, final_result: bool = False) -> Dict[str, Any]:
        """
        Retrieves the last task assignment record.

        Args:
            app_run_id (int): The ID of the app run.
            level (int): The level of the edge.
            node_id (str): The ID of the node.
            final_result (bool): Whether to get the final result. If True, includes task_id in the conditions.

        Returns:
            Dict[str, Any]: The last task assignment record.
        """
        conditions = [
            {"column": "app_run_id", "value": app_run_id},
            {"column": "level", "value": level},
            {"column": "node_id", "value": node_id},
            {"column": "correct_output", "value": 0}
        ]
        
        if final_result:
            conditions.append({"column": "task_id", "op": "is null"})
        
        last_assignment = self.select_one(
            columns='*',
            conditions=conditions,
            order_by='id DESC'
        )
        return last_assignment
    
    def get_previous_task_executions(self, node_exec_id: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Retrieves all task execution records before a given node execution record, and the latest execution record of the source node.

        Args:
            node_exec_id (int): The ID of the node execution record.

        Returns:
            Tuple[Dict[str, Any], List[Dict[str, Any]]]: A tuple containing:
                - The latest execution record of the source node.
                - A list of task execution records before the given node execution record.
        """
        current_record = self.select_one(
            columns=['app_run_id', 'level', 'edge_id', 'pre_node_id'],
            conditions=[{"column": "id", "value": node_exec_id}]
        )

        if not current_record:
            return None, []

        parent_last_execution = self.select_one(
            columns='*',
            conditions=[
                {"column": "app_run_id", "value": current_record["app_run_id"]},
                {"column": "level", "value": current_record["level"]},
                {"column": "node_id", "value": current_record["pre_node_id"]}
            ],
            order_by='id DESC'
        )

        if not parent_last_execution:
            return None, []

        node_graph = parent_last_execution.get("node_graph", {})
        input_value = node_graph.get("data", {}).get("input", {}).get("value", "")
        match = re.search(r'<<([0-9a-fA-F\-]+)\.outputs\.output>>', input_value)
        source_node_id = match.group(1) if match else None

        if not source_node_id:
            return None, []

        source_node_execution = self.select_one(
            columns='*',
            conditions=[
                {"column": "app_run_id", "value": current_record["app_run_id"]},
                {"column": "node_id", "value": source_node_id},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ],
            order_by='id DESC'
        )

        previous_executions = self.select(
            columns='*',
            conditions=[
                {"column": "id", "op": "<", "value": node_exec_id},
                {"column": "app_run_id", "value": current_record["app_run_id"]},
                {"column": "level", "value": current_record["level"]},
                {"column": "edge_id", "value": current_record["edge_id"]},
                {"column": "pre_node_id", "value": current_record["pre_node_id"]},
                {"column": "correct_output", "value": 0},
                {"column": "status", "value": 3}
            ]
        )

        return source_node_execution, previous_executions