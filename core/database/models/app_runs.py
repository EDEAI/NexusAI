from core.database import MySQL
from typing import Any, Dict, List
import math
from config import settings

class AppRuns(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "app_runs"
    """
    Indicates whether the `app_runs` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True


    def get_workflow_running_count(self, workflow_id: int) -> int:
        """
        Gets the count of running app runs for a specific workflow.

        :param workflow_id: The ID of the workflow.
        :return: The count of running app runs for the specified workflow.
        """
        result = self.select(
            aggregates={"id": "count"},
            conditions=[
                {"column": "workflow_id", "value": workflow_id},
                {"column": "status", "op": "<", "value": 3}
            ]
        )
        return result[0]["count_id"] if result else 0

    def get_runnable_workflow_runs(self) -> List[Dict[str, Any]]:
        """
        Retrieves all runnable workflow runs that are associated with their respective workflows.

        :return: A list of dictionaries, each representing a runnable workflow run along with its associated workflow details.
        """
        list = self.select(
            columns=['id AS app_run_id', 'user_id', 'app_id', 'workflow_id', 'type', 'name AS run_name', 'graph', 'inputs', 'knowledge_base_mapping',
                'level', 'context', 'completed_edges', 'skipped_edges', 'status', 'completed_steps', 'actual_completed_steps', 'need_human_confirm', 'outputs', 'elapsed_time', 
                'prompt_tokens', 'completion_tokens', 'total_tokens', 'embedding_tokens', 'reranking_tokens', 'total_steps', 'created_time', 'finished_time', 
                'apps.team_id', 'apps.user_id AS app_user_id', 'apps.name AS app_name', 'apps.icon', "apps.avatar", 'apps.icon_background'],
            joins=[
                ('inner', 'workflows', 'app_runs.workflow_id = workflows.id'),
                ('inner', 'apps', 'app_runs.app_id = apps.id')
            ],
            conditions=[
                {"column": "status", "value": 1},
                {"column": "workflows.status", "value": 1},
                {"column": "apps.status", "value": 1},
                [
                    {"column": "need_human_confirm", "value": 0, 'logic': 'or'},
                    {"column": "need_correct_llm", "value": 1},
                ]
            ],
        )

        for item in list:
            if item.get('avatar'):
                item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

        return list

    def get_running_app_run(self, app_run_id: int) -> Dict[str, Any]:
        """
        Retrieves a running app run by its ID.

        :param app_run_id: The ID of the running app run.
        :return: A dictionary representing the running app run.
        """
        return self.select_one(
            columns=['id AS app_run_id', 'user_id', 'app_id', 'workflow_id', 'type', 'level', 'context', 'completed_steps', 'actual_completed_steps', 'completed_edges', 'status', 'elapsed_time',
                'prompt_tokens', 'completion_tokens', 'total_tokens', 'embedding_tokens', 'reranking_tokens', 'total_steps', 'created_time', 'finished_time'],
            conditions=[{"column": "id", "value": app_run_id}, {"column": "status", "op": "in", "value": [2, 4]}]
        )

    def get_running_app_run_ai(self, app_run_id: int) -> Dict[str, Any]:
        """
        Retrieves a running app run by its ID.

        :param app_run_id: The ID of the running app run.
        :return: A dictionary representing the running app run.
        """
        return self.select_one(
            columns=['id AS app_run_id', 'user_id', 'app_id', 'workflow_id', 'type', 'level', 'context', 'completed_steps', 'actual_completed_steps', 'completed_edges', 'status', 'elapsed_time',
                'prompt_tokens', 'completion_tokens', 'total_tokens', 'embedding_tokens', 'reranking_tokens', 'total_steps', 'created_time', 'finished_time'],
            conditions=[{"column": "id", "value": app_run_id}, {"column": "status", "value": 2}]
        )

    def get_backlogs_list(self, data: Dict[str, Any]):
        """
        Get backlogs list

        :param data: dictionary containing filter conditions
        """
        conditions = [
            {"column": "apps.status", "value": 1},
            {"column": "app_runs.workflow_id", "op": ">", "value": 0},
            [
                {"column": "app_node_executions.status", "op": ">", "value": 2, 'logic': 'or'},
                [
                    {"column": "app_node_executions.status", "value": 2},
                    {"column": "app_node_executions.node_type", "value": "human"}
                ]
            ],
            {'column': 'app_node_executions.correct_output', 'value': 0},
            {'column': 'app_node_executions.condition_id', 'op': 'is null'},
        ]
        need_human_confirm = data.get('need_human_confirm', None)
        if need_human_confirm is not None:
            conditions.append({"column": "app_node_executions.need_human_confirm", "value": data['need_human_confirm']})

        if data['user_id'] > 0:
            conditions.append({"column": "app_node_user_relation.user_id", "value": data['user_id']})
        else:
            conditions.append({"column": "app_node_user_relation.user_id", "value": 0})

        total_count = self.select(
            aggregates = {"id": "count"},
            joins=[
                ["inner", "apps", "app_runs.app_id = apps.id"],
                ["inner", "app_node_user_relation", "app_node_user_relation.app_run_id = app_runs.id"],
                ["inner", "app_node_executions", "app_node_executions.node_id = app_node_user_relation.node_id and app_node_executions.app_run_id = app_runs.id"]
            ],
            conditions=conditions
        )[0]["count_id"]

        list = self.select(
            columns=[
                'app_runs.id AS app_run_id', 
                'app_runs.name AS app_run_name', 
                'apps.id AS app_id',
                'apps.name AS app_name', 
                'apps.mode', 
                'app_node_user_relation.node_id',
                'app_node_executions.node_graph', 
                'app_node_executions.node_name', 
                'app_node_executions.id AS exec_id', 
                'app_node_executions.need_human_confirm', "apps.avatar",
                'apps.icon', 
                'apps.icon_background'],
            joins= [
                ["inner", "apps", "app_runs.app_id = apps.id"],
                ["inner", "app_node_user_relation", "app_node_user_relation.app_run_id = app_runs.id"],
                ["inner", "app_node_executions", "app_node_executions.node_id = app_node_user_relation.node_id and app_node_executions.app_run_id = app_runs.id"]
            ],
            conditions=conditions,
            order_by = "app_node_executions.id DESC",
            limit = data['page_size'],
            offset = (data['page'] - 1) * data['page_size']
        )

        for item in list:
            if item.get('avatar'):
                item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

        # Add additional query to count records with need_human_confirm == 1
        human_confirm_total = self.select(
            aggregates={"id": "count"},
            joins=[
                ["inner", "apps", "app_runs.app_id = apps.id"],
                ["inner", "app_node_user_relation", "app_node_user_relation.app_run_id = app_runs.id"],
                ["inner", "app_node_executions", "app_node_executions.node_id = app_node_user_relation.node_id and app_node_executions.app_run_id = app_runs.id"]
            ],
            conditions=conditions + [{"column": "app_node_executions.need_human_confirm", "value": 1}]
        )[0]["count_id"]

        return {
            "list": list,
            "total_count": total_count,
            "human_confirm_total": human_confirm_total,
            "total_pages": math.ceil(total_count / data['page_size']),
            "page": data['page'],
            "page_size": data['page_size']
        }

    def get_workflow_log(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get workflow log

        :param data: dictionary containing filter conditions
        """
        conditions = [
            {"column": "app_runs.workflow_id", "op": ">", "value": 0}
        ]

        if 'user_id' in data:
            conditions.append([
                {"column": "apps.user_id", "value": data['user_id'], 'logic': 'or'},
                {"column": "app_runs.user_id", "value": data['user_id']}
            ])

        list = self.select(
            columns=['app_runs.id AS app_run_id', 'apps.name AS apps_name', 'app_runs.name AS app_runs_name',
                     'app_runs.workflow_id', 'app_runs.created_time', 'app_runs.elapsed_time', 'app_runs.status',
                     'app_runs.completed_steps', 'app_runs.total_steps', 'app_runs.need_human_confirm', 'apps.icon', "apps.avatar", 'apps.icon_background'],
            joins=[('inner', 'apps', 'app_runs.app_id = apps.id')],
            conditions=conditions,
            order_by = "app_runs.id DESC",
            limit=data['page_size']
        )

        for item in list:
            if item.get('avatar'):
                item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

        return list

    def increment_steps(self, app_run_id: int) -> bool:
        """
        Increments the completed_steps and total_steps field by 1 for the specified app run.

        :param app_id: The ID of the app run to update.
        :return: True if the update affected one or more rows, False otherwise.
        """
        sql = (
            f'UPDATE {self.table_name} '
            'SET '
            '   completed_steps = completed_steps + 1,'
            '   total_steps = total_steps + 1,'
            '   updated_time = NOW() '
            f'WHERE id = {app_run_id}'
        )
        result = self.execute_query(sql)
        return result.rowcount > 0

    def increment_token_usage(
        self,
        app_run_id: int,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int
    ) -> bool:
        """
        Increments the token usage fields for the specified app run.

        :param app_run_id: The ID of the app run to update
        :param prompt_tokens: Number of prompt tokens to add
        :param completion_tokens: Number of completion tokens to add  
        :param total_tokens: Number of total tokens to add
        :return: True if the update affected one or more rows, False otherwise
        """
        sql = (
            f'UPDATE {self.table_name} '
            'SET '
            f'  prompt_tokens = prompt_tokens + {prompt_tokens},'
            f'  completion_tokens = completion_tokens + {completion_tokens},'
            f'  total_tokens = total_tokens + {total_tokens},'
            '   updated_time = NOW() '
            f'WHERE id = {app_run_id}'
        )
        result = self.execute_query(sql)
        return result.rowcount > 0

    def get_search_app_run_team_id(self, app_run_id) -> Dict[str, Any]:
        """
        Gets the count of running app runs for a specific workflow.

        :param app_run_id: The ID of the app_run.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing task data.
        """
        result = self.select_one(
            columns=[
                "users.team_id", "users.id", "app_runs.user_id"
            ],
            joins=[
                ["left", "users", "users.id = app_runs.user_id"]
            ],
            conditions=[
                {"column": "app_runs.id", "value": app_run_id}
            ]
        )
        return result

    def get_app_run_info(self, app_run_id: int, user_id: int) -> Dict[str, Any]:
        return self.select_one(
            columns=["id"],
            conditions=[
                {"column": "id", "value": app_run_id},
                {"column": "user_id", "value": user_id}
            ]
        )

    def all_agent_log_list(self, page: int = 1, page_size: int = 10, user_id: int = 0, agent_id: List[int] = None):
        """
        Retrieves a list of chat rooms with pagination, filtering by user ID and chat room name.

        :param page: The page number for pagination.
        :param page_size: The number of items per page.
        :param agent_id: The ID of the agent (from the agent table) whose messages are to be retrieved.
        Defaults to 0, which may imply no specific agent is targeted.
        :type agent_id: int

        :param user_id: The ID of the user whose messages are to be retrieved.
        Defaults to 0, which may imply no specific user is targeted.
        :type user_id: int
        :return: A dictionary containing the list of chat rooms, total count, total pages, current page, and page size.
        """
        conditions = [
            # {"column": "app_runs.user_id", "value": user_id},

            [
                {"column": "apps.user_id", "value": user_id, 'logic': 'or'},
                {"column": "app_runs.user_id", "value": user_id}
            ],
            # {"column": "app_runs.agent_id", "value": agent_id},
            {"column": "app_runs.agent_id", 'op': 'in', 'value': agent_id},
            {'column': 'app_runs.status', 'op': 'in', 'value': [3, 4]},
            {'column': 'app_runs.app_id', 'op': '>', 'value': 0}
        ]

        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions,
            joins=[
                ["left", "apps", 'apps.id = app_runs.app_id'],
                ["left", "users", "users.id = app_runs.user_id"]
            ]
        )["count_id"]

        app_run_list = []
        if total_count > 0:
            app_run_list = self.select(
                columns=['users.nickname as nickname', 'app_runs.id', 'app_runs.user_id', 'app_runs.app_id', 'app_runs.agent_id', 'app_runs.workflow_id', 'app_runs.dataset_id', 'app_runs.tool_id', 'app_runs.chatroom_id', 'app_runs.type', 'app_runs.name', 'app_runs.graph', 'app_runs.inputs', 'app_runs.raw_user_prompt', 'app_runs.knowledge_base_mapping', 'app_runs.level', 'app_runs.context', 'app_runs.completed_edges', 'app_runs.skipped_edges', 'app_runs.status', 'app_runs.completed_steps', 'app_runs.actual_completed_steps', 'app_runs.need_human_confirm', 'app_runs.need_correct_llm', 'app_runs.error', 'app_runs.outputs', 'app_runs.elapsed_time', 'app_runs.prompt_tokens', 'app_runs.completion_tokens', 'app_runs.total_tokens', 'app_runs.embedding_tokens', 'app_runs.reranking_tokens', 'app_runs.total_steps', 'app_runs.created_time', 'app_runs.updated_time', 'app_runs.finished_time'],
                joins=[
                    ["left", "apps", 'apps.id = app_runs.app_id'],
                    ["left", "users", "users.id = app_runs.user_id"]
                ],
                conditions=conditions,
                order_by="id DESC",
                limit=page_size,
                offset=(page - 1) * page_size
            )
            if app_run_list:
                for log in app_run_list:
                    if 'status' in log:
                        status = log['status']
                        if status in (1, 2):
                            log['status'] = 1
                        elif status == 3:
                            log['status'] = 2
                        elif status == 4:
                            log['status'] = 3

        return {
            "list": app_run_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }
