from collections import defaultdict
from typing import Any, Dict, List
from core.database import MySQL
from core.database.models.app_node_executions import AppNodeExecutions
from core.database.models.users import Users
from core.database.models.app_node_user_relation import AppNodeUserRelation
from core.database.models.upload_files import UploadFiles
from core.database.models.chatroom_messages import ChatroomMessages
import math, json
from time import time
from datetime import datetime
from sqlalchemy.sql import text
from core.database.models.app_runs import AppRuns
from core.workflow.variables import create_variable_from_dict, get_first_variable_value, flatten_variable_with_values
from core.workflow.recursive_task import create_recursive_task_category_from_dict
from languages import get_language_content
import os
from config import settings
from core.database.models.agents import Agents
from core.database.models.chatroom_agent_relation import ChatroomAgentRelation
from core.database.models.chatrooms import Chatrooms


class Workspaces(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "apps"

    """
    Indicates whether the `apps` table has an `updated_time` column that tracks when a record was last updated
    """
    have_updated_time = True

    def get_workspace_list(self, page: int = 1, page_size: int = 10, uid: int = 0, team_id: int = 0):
        """
        Get Studio - Recent active items on the homepage, including Agent ChatRooms and WorkflowProcesses.

        :param page: The page number for pagination (default is 1).
        :param page_size: The number of records per page (default is 10).
        :param uid: The user ID to filter records by (default is 0).
        :param team_id: The team ID to filter records by (default is 0).

        :return: A dictionary containing:
            - "list": A list of dictionaries, each representing an app with its details, including app_id, process_name, workflow_id, chatroom_id, agent_id, and last_agent_name.
            - "total_count": The total number of matching records.
            - "total_pages": The total number of pages based on the page size.
            - "page": The current page number.
            - "page_size": The number of records per page.
        """
        query_count = f"""
            SELECT COUNT(*)
            FROM apps
            INNER JOIN app_runs ON app_runs.app_id = apps.id
            INNER JOIN (
                SELECT MAX(id) AS max_id, app_id
                FROM app_runs 
                GROUP BY app_id
            ) AS last_runs ON app_runs.id = last_runs.max_id
            WHERE apps.user_id = {uid} AND
                  apps.team_id = {team_id} AND
                  apps.status IN ('1', '2') AND
                  (app_runs.agent_id != 0 OR app_runs.chatroom_id != 0 OR app_runs.workflow_id != 0) AND
                    apps.mode In('1','2','5')AND (
                        app_runs.chatroom_id = 0
                        OR EXISTS (
                            SELECT 1 FROM chatrooms
                            WHERE chatrooms.id = app_runs.chatroom_id
                            AND chatrooms.chat_agent_id = 0
                            AND chatrooms.is_temporary = 0
                        )
                )
        """
        total_count_result = self.execute_query(query_count)

        total_count = total_count_result.scalar()
        check_page = (page - 1) *page_size
        query = f"""
            SELECT apps.id AS app_id,
                   app_runs.name AS process_name,
                   apps.name,
                   apps.icon,
                   apps.avatar,
                   apps.icon_background,
                   app_runs.workflow_id,
                   app_runs.chatroom_id,
                   app_runs.agent_id,
                   app_runs.id AS app_runs_id
            FROM apps
            INNER JOIN app_runs ON app_runs.app_id = apps.id
            INNER JOIN (
                SELECT MAX(id) AS max_id, app_id
                FROM app_runs 
                GROUP BY app_id
            ) AS last_runs ON app_runs.id = last_runs.max_id
            WHERE apps.user_id = {uid} AND
                  apps.team_id = {team_id} AND
                  apps.status IN ('1', '2') AND
                  (app_runs.agent_id != 0 OR app_runs.chatroom_id != 0 OR app_runs.workflow_id != 0)  AND apps.mode In('1','2','5')
                AND (
                        app_runs.chatroom_id = 0
                        OR EXISTS (
                            SELECT 1 FROM chatrooms
                            WHERE chatrooms.id = app_runs.chatroom_id
                            AND chatrooms.chat_agent_id = 0
                            AND chatrooms.is_temporary = 0
                        )
                )
            ORDER BY app_runs.updated_time DESC
            LIMIT {check_page}, {page_size}
            """
        app_list_result = self.execute_query(query)
        app_list = app_list_result.mappings().all()
        if app_list:
            app_list = [dict(app) for app in app_list]

            for app in app_list:
                if app.get('avatar'):
                    app['avatar'] = f"{settings.STORAGE_URL}/upload/{app['avatar']}"
                else:
                    app['avatar'] = f"{settings.ICON_URL}/head_icon/{app['icon']}.svg"
                app['last_agent_name'] = ''
                if app["workflow_id"] > 0:
                    app["type"] = 3
                    app["process_name"] = f"{get_language_content('recently_active_process')}【{app['process_name']}】"
                else:
                    app["process_name"] = ''
                if app["chatroom_id"] > 0:
                    app["type"] = 2
                    last_agent = ChatroomMessages().select_one(
                        joins=[
                            ["inner", "agents", 'agents.id = chatroom_messages.agent_id'],
                            ["inner", "apps", "agents.app_id = apps.id"]
                        ],
                        columns=["apps.name"],
                        conditions=[
                            {"column": "chatroom_messages.chatroom_id", "value": app['chatroom_id']},
                            {'column': 'chatroom_messages.agent_id', 'op': '>', 'value': 0}
                        ],
                        order_by="chatroom_messages.id DESC",
                        limit=1
                    )
                    if last_agent:
                        app['last_agent_name'] = f"{get_language_content('recently_active_agent')}【{last_agent['name']}】"

                    agent_relations = ChatroomAgentRelation().select(
                        columns=["agent_id"],
                        conditions=[
                            {"column": "chatroom_id", "value": app['chatroom_id']}
                        ],
                        order_by="id DESC"
                    )
                    agent_ids = [rel['agent_id'] for rel in agent_relations if rel['agent_id'] > 0]
                    app['agents_data'] = []
                    if agent_ids:
                        agents = Agents().select(
                            columns=["apps.avatar","apps.icon"],
                            conditions=[
                                {"column": "id", "op": "in", "value": agent_ids}
                            ],
                            joins=[
                                ["left", "apps", "apps.id = agents.app_id"],
                            ]
                        )
                        # Build a mapping from agent_id to agent information
                        for agent in agents:
                            if agent.get('avatar'):
                                avatar_url = f"{settings.STORAGE_URL}/upload/{agent['avatar']}"
                            # else:
                                # avatar_url = ''
                            else:
                                avatar_url = f"{settings.ICON_URL}/head_icon/{agent['icon']}.svg"
                            app['agents_data'].append({"avatar": avatar_url,"icon": agent.get("icon")})
                if app["agent_id"] > 0:
                    app["type"] = 1

        return {
            "list": app_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def get_workflow_log_info(self, workflows_id: int = 0, app_runs_id: int = 0):

        """
        Get Workflow log details.

        :param workflows_id: The workflow ID to filter log details by (default is 0).
        :param app_runs_id: The specific run ID of the application to retrieve logs for (default is 0).

        :return: A dictionary containing:
            - "list": A list of node execution logs with details such as node name, graph, inputs, status, error, and execution times.
            - "app_run_data": A list of application run details including workflow ID, run status, completed steps, error info, token counts, and timestamps.
        """
        from core.llm import get_serialized_prompt_from_messages
        
        app_node_executions = AppNodeExecutions()
        conditions = [
            {"column": "app_node_executions.workflow_id", "value": workflows_id},
            {"column": "app_node_executions.app_run_id", "value": app_runs_id},
            {"column": "app_node_executions.correct_output", "value": 0}
        ]

        app_node_list = app_node_executions.select(
            joins=[
                ["inner", "app_runs", 'app_runs.id = app_node_executions.app_run_id'],
                ["inner", "apps", 'app_runs.app_id = apps.id']
            ],
            columns=["app_node_executions.id", "app_node_executions.level", "app_node_executions.child_level",
                     "app_node_executions.edge_id", "app_node_executions.pre_node_id", "app_node_executions.node_id", "app_node_executions.node_name",
                     "app_node_executions.node_type", "app_node_executions.node_graph", "app_node_executions.inputs",
                     "app_node_executions.model_data AS mod_data", "app_node_executions.task_id",
                     "app_node_executions.status",
                     "app_node_executions.error", "app_node_executions.outputs", "app_node_executions.elapsed_time",
                     "app_node_executions.created_time", "app_node_executions.updated_time",
                     "app_node_executions.finished_time","apps.icon_background", "apps.icon", "apps.avatar","app_node_executions.need_human_confirm","app_node_executions.user_id"],
            conditions=conditions
        )

        app_run_info = []
        app_node_result = []
        if app_node_list:
            child_executions_dict = defaultdict(list)
            recursive_task_executions = {}
            # Dictionary to map edge_id to recursive task execution nodes
            edge_id_to_recursive_task = {}
            
            from api.utils.common import extract_file_list_from_skill_output
            for app_node in app_node_list:
                if app_node.get('avatar'):
                    app_node['avatar'] = f"{settings.STORAGE_URL}/upload/{app_node['avatar']}"
                else:
                    app_node['avatar'] = f"{settings.ICON_URL}/head_icon/{app_node['icon']}.svg"
                if app_node['need_human_confirm'] == 1:
                    users = Users()
                    app_node_user = AppNodeUserRelation()
                    app_node_user_ids = app_node_user.get_node_user_ids(app_runs_id, app_node['node_id'])
                    app_node['human_confirm_info'] = []
                    for userId in app_node_user_ids:
                        user_info = users.get_user_by_id(userId)
                        app_node['human_confirm_info'].append({
                            'user_id': user_info['id'],
                            'nickname': user_info['nickname']
                        })
                if app_node['child_level'] > 0 and app_node['node_type'] == 'recursive_task_execution':
                    continue

                # Store recursive task execution nodes by edge_id for later reference
                if app_node['node_type'] == 'recursive_task_execution':
                    recursive_task_executions[f"{app_node['level']}-{app_node['node_id']}"] = app_node
                    # Also store by edge_id if available
                    if app_node.get('edge_id'):
                        edge_id_to_recursive_task[app_node['edge_id']] = app_node
                    continue

                if inputs := app_node.get('inputs'):
                    inputs = create_variable_from_dict(inputs)
                    inputs = flatten_variable_with_values(inputs)
                    app_node['inputs'] = inputs
                if outputs := app_node.get('outputs'):
                    app_node['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
                    if app_node['node_type'] in ['llm', 'agent']:
                        app_node['outputs_md'] = get_first_variable_value(create_variable_from_dict(outputs))
                    elif app_node['node_type'] == 'recursive_task_generation' or (app_node['node_type'] == 'recursive_task_execution' and not app_node['task_id']):
                        task_dict = json.loads(get_first_variable_value(create_variable_from_dict(outputs)))
                        app_node['outputs_md'] = create_recursive_task_category_from_dict(task_dict).to_markdown()
                    elif app_node['node_type'] in ['skill', 'custom_code', 'end']:
                        file_list = extract_file_list_from_skill_output(app_node['outputs'], app_node['node_graph']['data']['output'])
                        app_node['file_list'] = file_list
                    else:
                        app_node['outputs_md'] = None

                prompt_data = []
                if app_node["mod_data"] is not None:
                    messages = app_node["mod_data"]["messages"]
                    prompt_data = get_serialized_prompt_from_messages(messages)
                app_node["prompt_data"] = prompt_data
                app_node.pop("mod_data")

                app_node['child_executions'] = []

                # Check if this node should be linked to a recursive task execution node via edge_id
                if app_node['node_type'] != 'recursive_task_execution' and app_node.get('edge_id') and app_node['edge_id'] in edge_id_to_recursive_task:
                    parent_node = edge_id_to_recursive_task[app_node['edge_id']]
                    key = f"{parent_node['level']}-{parent_node['node_id']}"
                    child_executions_dict[key].append(app_node)
                else:
                    app_node_result.append(app_node)

            if recursive_task_executions:
                for _, node in recursive_task_executions.items():
                    app_node_result.append(node)
            app_node_result.sort(key=lambda x: x['id'])

            if child_executions_dict:
                for app_node in app_node_result:
                    app_node['child_executions'] = child_executions_dict.get(f"{app_node['level']}-{app_node['node_id']}", [])
                    if app_node['child_executions']:
                        app_node["prompt_data"] = []
                        app_node['elapsed_time'] = app_node_executions.get_task_total_data(app_runs_id, app_node['level'], app_node['node_id'])['total_elapsed_time']
                        task_result = app_node_executions.get_last_task_assignment(app_runs_id, app_node['level'], app_node['node_id'], True)
                        if not task_result:
                            last_assignment = app_node_executions.get_last_task_assignment(app_runs_id, app_node['level'], app_node['node_id'])
                            app_node['status'] = 2 if last_assignment['status'] != 4 else 4
                            app_node['error'] = last_assignment['error']
                            app_node['outputs'] = None
                            app_node['outputs_md'] = None
                            app_node['finished_time'] = None
                        else:
                            app_node['status'] = task_result['status']
                            app_node['error'] = task_result['error']
                            app_node['outputs'] = flatten_variable_with_values(create_variable_from_dict(task_result['outputs'])) if task_result['outputs'] else {}
                            if app_node['node_type'] in ['llm', 'agent'] and app_node['outputs']:
                                app_node['outputs_md'] = get_first_variable_value(create_variable_from_dict(task_result['outputs']))
                            elif app_node['node_type'] in ['recursive_task_generation', 'recursive_task_execution'] and app_node['outputs']:
                                task_dict = json.loads(get_first_variable_value(create_variable_from_dict(task_result['outputs'])))
                                app_node['outputs_md'] = create_recursive_task_category_from_dict(task_dict).to_markdown()
                            else:
                                app_node['outputs_md'] = None

            app_run_info = AppRuns().select(
                columns=[
                    "app_id", "workflow_id", "id AS app_run_id", "type", "level", "status", "error",
                    "completed_steps", "actual_completed_steps", "need_human_confirm", "elapsed_time", "prompt_tokens",
                    "completion_tokens", "total_tokens", "embedding_tokens", "reranking_tokens",
                    "total_steps", "finished_time", "created_time"
                ],
                conditions=[{'column': 'id', 'value': app_runs_id}]
            )
            if app_run_info:
                for log_run in app_run_info:
                    if 'status' in log_run:
                        app_runs_status = log_run['status']
                        if app_runs_status in (1, 2):
                            log_run['status'] = 1
                        elif app_runs_status == 3:
                            log_run['status'] = 2
                        elif app_runs_status == 4:
                            log_run['status'] = 3

        return {
            "list": app_node_result,
            "app_run_data": app_run_info
        }

    def get_workflow_process_log(self, page: int = 0, page_size: int = 0, show_status: int = 0, uid: int = 0):
        """
        Get workflow process logs with pagination and filtering options.

        Args:
            page (int): The page number for pagination (default is 0).
            page_size (int): Number of records per page (default is 0).
            show_status (int): Filter records by status (default is 0).
                - 0: All records
                - 1: Meeting-driven records
                - 2: Agent execution records
                - 3: Workflow execution records
            uid (int): User ID to filter records (default is 0).

        Returns:
            dict: A dictionary containing:
                - list (list): List of workflow process logs with details including:
                    - app_run_id: ID of the application run
                    - apps_name: Name of the application
                    - workflow_id: ID of the workflow
                    - status: Current status of the process
                    - chat_room_name: Name of the associated chatroom
                    - driver_id: ID of the driver record
                    - file_list: List of associated files
                - total_count (int): Total number of records
                - total_pages (int): Total number of pages
                - page (int): Current page number
                - page_size (int): Number of records per page
        """

        # Build base query conditions
        base_where = f"""
        WHERE (apps.user_id = {uid} OR app_runs.user_id = {uid})
        """

        if show_status == 0:
            # All records
            where_clause = f"""
            {base_where}
            AND (
                (app_runs.workflow_id > 0 OR app_runs.agent_id > 0)
                OR (app_runs.app_id = 0 AND app_runs.chatroom_id > 0)
            )
            """
        elif show_status == 1:
            # Meeting-driven records
            where_clause = f"""
            {base_where}
            AND app_runs.app_id = 0 
            AND app_runs.chatroom_id > 0
            """
        elif show_status == 2:
            # Agent execution records
            where_clause = f"""
            {base_where}
            AND app_runs.agent_id > 0 
            AND app_runs.chatroom_id = 0
            """
        elif show_status == 3:
            # Workflow execution records
            where_clause = f"""
            {base_where}
            AND app_runs.workflow_id > 0 
            AND app_runs.chatroom_id = 0
            """

        # Query for total count
        count_sql = f"""
        SELECT COUNT(*) as count
        FROM app_runs
        LEFT JOIN apps ON app_runs.app_id = apps.id
        LEFT JOIN chatroom_driven_records ON chatroom_driven_records.data_source_run_id = app_runs.id
        {where_clause}
        """
        
        total_count_result = self.execute_query(count_sql)
        total_count = total_count_result.scalar()

        offset = (page - 1) * page_size if page > 0 else 0
        # Query for list data
        list_sql = f"""
        SELECT 
            app_runs.id AS app_run_id,
            IFNULL(apps.name, '') AS apps_name,
            app_runs.name AS app_runs_name,
            IFNULL(app_runs.workflow_id, 0) AS workflow_id,
            app_runs.created_time,
            app_runs.elapsed_time,
            app_runs.status,
            app_runs.completed_steps,
            app_runs.total_steps,
            apps.mode,
            IFNULL(apps.icon_background, '') AS icon_background,
            IFNULL(apps.icon, '') AS icon,
            IFNULL(apps.avatar, '') AS avatar,
            IFNULL(app_runs.chatroom_id, 0) AS chatroom_id,
            IFNULL(app_runs.agent_id, 0) AS agent_id,
            IFNULL(apps.id, 0) AS app_id,
            IFNULL(app_runs.user_id, 0) AS user_id,
            IFNULL(users.nickname, '') AS nickname
        FROM app_runs
        LEFT JOIN apps ON app_runs.app_id = apps.id
        LEFT JOIN users ON app_runs.user_id = users.id
        {where_clause}
        ORDER BY app_runs.id DESC
        LIMIT {offset}, {page_size}
        """
        
        log_list_result = self.execute_query(list_sql)
        log_list = [dict(row._mapping) for row in log_list_result]

        if log_list:
            for log in log_list:
                if log.get('avatar'):
                    log['avatar'] = f"{settings.STORAGE_URL}/upload/{log['avatar']}"
                else:
                    log['avatar'] = f"{settings.ICON_URL}/head_icon/{log['icon']}.svg"
                # Meeting-driven record - status 1
                if log['app_id'] == 0 and log['chatroom_id'] > 0:
                    log['show_status'] = 1
                    # Get driver_id from chatroom_driven_records
                    driver_sql = f"""
                    SELECT id as driver_id
                    FROM chatroom_driven_records
                    WHERE data_source_run_id = {log['app_run_id']}
                    LIMIT 1
                    """
                    driver_result = self.execute_query(driver_sql)
                    driver_data = driver_result.mappings().first()
                    log['driver_id'] = driver_data['driver_id'] if driver_data else 0

                    # Get chatroom name
                    backup_sql = f"""
                        SELECT DISTINCT IFNULL(apps.name, '') as chat_room_name
                        FROM app_runs
                        INNER JOIN chatrooms ON app_runs.chatroom_id = chatrooms.id
                        INNER JOIN apps ON chatrooms.app_id = apps.id
                        WHERE app_runs.id = {log['app_run_id']}
                        """
                    backup_result = self.execute_query(backup_sql)
                    chat_room_data = backup_result.mappings().first()
                    log['chat_room_name'] = chat_room_data['chat_room_name'] if chat_room_data else ''
                    log['associated_chat_room_name'] = ''
                    
                    agent_relations = ChatroomAgentRelation().select(
                        columns=["agent_id"],
                        conditions=[
                            {"column": "chatroom_id", "value": log['chatroom_id']}
                        ],
                        order_by="id DESC"
                    )
                    

                    agent_ids = [rel['agent_id'] for rel in agent_relations if rel['agent_id'] > 0]
                    
                    
                    log['agents_data'] = []
                    if agent_ids:
                        agents = Agents().select(
                            columns=["apps.avatar","apps.icon"],
                            conditions=[
                                {"column": "id", "op": "in", "value": agent_ids}
                            ],
                            joins=[
                                ["left", "apps", "apps.id = agents.app_id"],
                            ]
                        )
                        
                        # Build a mapping from agent_id to agent information
                        for agent in agents:
                            if agent.get('avatar'):
                                avatar_url = f"{settings.STORAGE_URL}/upload/{agent['avatar']}"
                            # else:
                            #     avatar_url = ''
                            else:
                                avatar_url = f"{settings.ICON_URL}/head_icon/{agent['icon']}.svg"
                            log['agents_data'].append({"avatar": avatar_url,"icon": agent.get("icon")})
                        # for agent in agents:
                        #     if agent.get('avatar'):
                        #         agent['avatar'] = f"{settings.STORAGE_URL}/upload/{agent['avatar']}"
                        #     log['agents_data'].append(agent['avatar'])
                    
                    
                    # Get app name from agent or workflow
                    if log['agent_id'] > 0:
                        agent_sql = f"""
                        SELECT IFNULL(apps.name, '') as apps_name
                        FROM agents
                        INNER JOIN apps ON agents.app_id = apps.id
                        WHERE agents.id = {log['agent_id']}
                        """
                        agent_result = self.execute_query(agent_sql)
                        agent_data = agent_result.mappings().first()
                        log['apps_name'] = agent_data['apps_name'] if agent_data else ''
                        log['mode'] = 1
                    elif log['workflow_id'] > 0:
                        workflow_sql = f"""
                        SELECT IFNULL(apps.name, '') as apps_name
                        FROM workflows
                        INNER JOIN apps ON workflows.app_id = apps.id
                        WHERE workflows.id = {log['workflow_id']}
                        """
                        workflow_result = self.execute_query(workflow_sql)
                        workflow_data = workflow_result.mappings().first()
                        log['apps_name'] = workflow_data['apps_name'] if workflow_data else ''
                        log['mode'] = 2

                        workflows_id = log['workflow_id']
                        app_runs_id = log['app_run_id']
                        app_node_executions = AppNodeExecutions()
                        conditions = [
                            {"column": "app_node_executions.workflow_id", "value": workflows_id},
                            {"column": "app_node_executions.app_run_id", "value": app_runs_id},
                            {"column": "app_node_executions.correct_output", "value": 0},
                            {"column": "app_node_executions.node_type", "value": "end"}
                        ]

                        app_node_list = app_node_executions.select_one(
                            joins=[
                                ["inner", "app_runs", 'app_runs.id = app_node_executions.app_run_id'],
                                ["inner", "apps", 'app_runs.app_id = apps.id']
                            ],
                            columns=["app_node_executions.id", "app_node_executions.level", "app_node_executions.child_level",
                                    "app_node_executions.pre_node_id", "app_node_executions.node_id", "app_node_executions.node_name",
                                    "app_node_executions.node_type", "app_node_executions.node_graph", "app_node_executions.inputs",
                                    "app_node_executions.model_data AS mod_data", "app_node_executions.task_id",
                                    "app_node_executions.status",
                                    "app_node_executions.error", "app_node_executions.outputs", "app_node_executions.elapsed_time",
                                    "app_node_executions.created_time", "app_node_executions.updated_time",
                                    "app_node_executions.finished_time","apps.icon_background", "apps.icon","apps.avatar","app_node_executions.need_human_confirm","app_node_executions.user_id"],
                            conditions=conditions
                        )
                        log['file_list'] = []
                        if app_node_list and app_node_list.get('outputs'):
                            
                            if app_node_list.get('avatar'):
                                app_node_list['avatar'] = f"{settings.STORAGE_URL}/upload/{app_node_list['avatar']}"
                            else:
                                app_node_list['avatar'] = f"{settings.ICON_URL}/head_icon/{app_node_list['icon']}.svg"
                            if outputs := app_node_list.get('outputs'):
                                app_node_list['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
                                
                                from api.utils.common import extract_file_list_from_skill_output
                                file_list = extract_file_list_from_skill_output(app_node_list['outputs'], app_node_list['node_graph']['data']['output'])
                                log['file_list'] = file_list
                        start_time = time()
                        start_datetime_str = datetime.fromtimestamp(start_time) \
                            .replace(microsecond=0).isoformat(sep='_')
                        round_table_orientation_operation = get_language_content('round_table_orientation_operation')
                        log['app_runs_name'] = f"{round_table_orientation_operation}_{start_datetime_str}"
                # Agent execution record - status 2
                elif log['agent_id'] > 0:
                    log['show_status'] = 2
                    log['chat_room_name'] = ''
                    log['file_list'] = []
                    log['agents_data'] = []
                    log['driver_id'] = 0
                    find_chatroom_sql = f"""
                    SELECT chatroom_id
                    FROM chatroom_driven_records
                    WHERE data_driven_run_id = {log['app_run_id']}
                    LIMIT 1
                    """
                    find_chatroom = self.execute_query(find_chatroom_sql)
                    chatroom_data = find_chatroom.mappings().first()
                    if chatroom_data:
                    # Get chatroom name from chatrooms and apps tables
                        chatroom_name_sql = f"""
                        SELECT IFNULL(apps.name, '') as chat_room_name
                        FROM chatrooms
                        INNER JOIN apps ON chatrooms.app_id = apps.id
                        WHERE chatrooms.id = {chatroom_data['chatroom_id']}
                        LIMIT 1
                        """
                        chatroom_name_result = self.execute_query(chatroom_name_sql)
                        chatroom_name_data = chatroom_name_result.mappings().first()
                        log['associated_chat_room_name'] = chatroom_name_data['chat_room_name'] if chatroom_name_data else ''
                    else:
                        log['associated_chat_room_name'] = ''
                # Workflow execution record - status 3
                elif log['workflow_id'] > 0:
                    log['show_status'] = 3
                    log['chat_room_name'] = ''
                    log['driver_id'] = 0
                    log['agents_data'] = []
                    workflows_id = log['workflow_id']
                    app_runs_id = log['app_run_id']
                    find_chatroom_sql = f"""
                    SELECT chatroom_id
                    FROM chatroom_driven_records
                    WHERE data_driven_run_id = {log['app_run_id']}
                    LIMIT 1
                    """
                    find_chatroom = self.execute_query(find_chatroom_sql)
                    chatroom_data = find_chatroom.mappings().first()
                    if chatroom_data:
                    # Get chatroom name from chatrooms and apps tables
                        chatroom_name_sql = f"""
                        SELECT IFNULL(apps.name, '') as chat_room_name
                        FROM chatrooms
                        INNER JOIN apps ON chatrooms.app_id = apps.id
                        WHERE chatrooms.id = {chatroom_data['chatroom_id']}
                        LIMIT 1
                        """
                        chatroom_name_result = self.execute_query(chatroom_name_sql)
                        chatroom_name_data = chatroom_name_result.mappings().first()
                        log['associated_chat_room_name'] = chatroom_name_data['chat_room_name'] if chatroom_name_data else ''
                    else:
                        log['associated_chat_room_name'] = ''
                    
                    app_node_executions = AppNodeExecutions()
                    node_type = 'end'
                    conditions = [
                        {"column": "app_node_executions.workflow_id", "value": workflows_id},
                        {"column": "app_node_executions.app_run_id", "value": app_runs_id},
                        {"column": "app_node_executions.correct_output", "value": 0},
                        {"column": "app_node_executions.node_type", "value": node_type}
                    ]

                    app_node_list = app_node_executions.select_one(
                        joins=[
                            ["inner", "app_runs", 'app_runs.id = app_node_executions.app_run_id'],
                            ["inner", "apps", 'app_runs.app_id = apps.id']
                        ],
                        columns=["app_node_executions.id", "app_node_executions.level", "app_node_executions.child_level",
                                "app_node_executions.pre_node_id", "app_node_executions.node_id", "app_node_executions.node_name",
                                "app_node_executions.node_type", "app_node_executions.node_graph", "app_node_executions.inputs",
                                "app_node_executions.model_data AS mod_data", "app_node_executions.task_id",
                                "app_node_executions.status",
                                "app_node_executions.error", "app_node_executions.outputs", "app_node_executions.elapsed_time",
                                "app_node_executions.created_time", "app_node_executions.updated_time",
                                "app_node_executions.finished_time","apps.icon_background", "apps.icon","apps.avatar","app_node_executions.need_human_confirm","app_node_executions.user_id"],
                        conditions=conditions
                    )
                    log['file_list'] = []
                    if app_node_list and app_node_list.get('outputs'):
                        if app_node_list.get('avatar'):
                            app_node_list['avatar'] = f"{settings.STORAGE_URL}/upload/{app_node_list['avatar']}"
                        else:
                            app_node_list['avatar'] = f"{settings.ICON_URL}/head_icon/{app_node_list['icon']}.svg"
                        if outputs := app_node_list.get('outputs'):
                            app_node_list['outputs'] = flatten_variable_with_values(create_variable_from_dict(outputs))
                            
                            from api.utils.common import extract_file_list_from_skill_output
                            file_list = extract_file_list_from_skill_output(app_node_list['outputs'], app_node_list['node_graph']['data']['output'])
                            log['file_list'] = file_list
                    start_time = time()
                    start_datetime_str = datetime.fromtimestamp(start_time) \
                        .replace(microsecond=0).isoformat(sep='_')
                    round_table_orientation_operation = get_language_content('round_table_orientation_operation')
                    if log['chatroom_id'] > 0:
                        log['app_runs_name'] = f"{round_table_orientation_operation}_{start_datetime_str}"
                else:
                    log['show_status'] = 0
                    log['chat_room_name'] = ''
                    log['file_list'] = []
                    log['agents_data'] = []
                    log['driver_id'] = 0
                    log['associated_chat_room_name'] = ''
                # Default status handling
                if log['status'] in (1, 2):
                    log['status'] = 1
                elif log['status'] == 3:
                    log['status'] = 2
                elif log['status'] == 4:
                    log['status'] = 3

        return {
            "list": log_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def get_workspace_workflow_log_list(self, page: int = 1, page_size: int = 10, app_id: int = 0,
                                        app_runs_name: str = "", app_runs_status: int = 0, uid: int = 0):

        """
        Get Workflow log list.

        :param page: The page number for pagination (default is 1).
        :param page_size: The number of records per page (default is 10).
        :param app_id: The application ID to filter logs by (default is 0).
        :param app_runs_name: A string used to search for logs with a specific workflow name (default is "").
        :param app_runs_status: The status of the workflow run to filter logs by (1 for running, 2 for completed, 3 for failed) (default is 0).
        :param uid: The user ID to filter logs by (default is 0).

        :return: A dictionary containing:
            - "list": A list of workflow log dictionaries with details such as app_id, app_runs_id, workflow name, type, status, and other related metadata.
            - "total_count": The total number of matching logs.
            - "total_pages": The total number of pages based on the page size.
            - "page": The current page number.
            - "page_size": The number of records per page.
        """

        conditions = [
            {"column": "apps.user_id", "value": uid},
            {"column": "apps.id", "value": app_id},
            {"column": "apps.mode", "value": 2},
            {"column": "apps.status", "op": "in", "value": [1, 2]}
        ]
        if app_runs_name:
            conditions.append({"column": "app_runs.name", "op": "like", "value": "%" + app_runs_name + "%"})

        if app_runs_status == 1:
            conditions.append({"column": "app_runs.status", "op": "in", "value": [1, 2]})
        elif app_runs_status == 2:
            conditions.append({"column": "app_runs.status", "op": "=", "value": 3})
        elif app_runs_status == 3:
            conditions.append({"column": "app_runs.status", "op": "=", "value": 4})
        else:
            pass

        total_count = self.select(
            aggregates={"id": "count"},
            joins=[
                ["left", "app_runs", "apps.id = app_runs.app_id"]
            ],
            conditions=conditions,
        )[0]["count_id"]

        list = self.select(
            columns=["apps.user_id", "apps.id AS app_id","apps.icon_background", "apps.icon","apps.avatar",
                     "apps.name", "app_runs.id AS app_runs_id", "app_runs.name AS app_runs_name",
                     "app_runs.type AS app_runs_type",
                     "app_runs.level AS app_runs_level", "app_runs.created_time", "app_runs.updated_time",
                     "app_runs.elapsed_time", "app_runs.finished_time", "app_runs.workflow_id",
                     "app_runs.status AS app_runs_status", "app_runs.completed_steps", "app_runs.total_steps",
                     "app_runs.total_tokens","apps.icon_background", "apps.icon",
                     "users.nickname"
                     ],
            joins=[
                ["left", "app_runs", "apps.id = app_runs.app_id"],
                ["left", "users", "users.id = app_runs.user_id"]
            ],
            conditions=conditions,
            order_by="app_runs.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        if list:
            for log in list:
                if log.get('avatar'):
                    log['avatar'] = f"{settings.STORAGE_URL}/upload/{log['avatar']}"
                else:
                    log['avatar'] = f"{settings.ICON_URL}/head_icon/{log['icon']}.svg"
                if 'app_runs_status' in log:
                    status = log['app_runs_status']
                    if status in (1, 2):
                        log['app_runs_status'] = 1
                    elif status == 3:
                        log['app_runs_status'] = 2
                    elif status == 4:
                        log['app_runs_status'] = 3

        return {
            "list": list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }
