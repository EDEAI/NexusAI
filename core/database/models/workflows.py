from datetime import datetime
import itertools
import math
from typing import Any, Dict, Optional

from sqlalchemy.exc import SQLAlchemyError

from core.database import MySQL

from core.database.models.agents import Agents
from core.database.models.app_workflow_relation import AppWorkflowRelations
from core.database.models.apps import Apps

from core.database import SQLDatabase
from core.database.models.custom_tools import CustomTools
from core.database.models.datasets import Datasets
from core.helper import generate_api_token, encrypt_id, format_iso_time
from hashlib import md5

from languages import get_language_content
from config import settings


class Workflows(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "workflows"
    """
    Indicates whether the `workflows` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    publish_status = 1

    w_publish_status = 0

    del_status = 3

    def get_workflow_app(self, workflow_id: int) -> Dict[str, Any]:
        """
        Retrieves the workflow associated with the app.

        :param workflow_id: The ID of the workflow.
        :return: A dictionary representing the workflow associated with the app.
        """
        return self.select_one(
            columns=['apps.id AS app_id', 'apps.name', 'apps.description', 'apps.enable_api', 'apps.is_public',
                     'apps.created_time', 'apps.updated_time',
                     'id AS workflow_id', 'graph', 'publish_status', 'published_time'],
            joins=[('inner', 'apps', 'workflows.app_id = apps.id')],
            conditions=[
                {'column': 'id', 'value': workflow_id},
                {'column': 'status', 'value': 1},
                {'column': 'apps.status', 'value': 1}
            ]
        )

    def workflows_info(self, app_id: int, publish_status: int, uid: int, team_id: int):
        # get app
        apps_model = Apps()
        app = apps_model.select_one(
            columns=["id AS app_id", "user_id", "name", "description",
                     "icon", "icon_background", "mode",
                     "is_public", "created_time", "status", "publish_status",
                     "enable_api", "api_token"],
            conditions=[
                {"column": "id", "value": app_id},
                {"column": "team_id", "value": team_id},
                {"column": "mode", "value": 2},  # 2: workflow
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not app:
            return {"status": 2, "message": "app data fail"}

        if app["user_id"] != uid:
            if publish_status == 0:
                return {"status": 2, "message": "Only creators can view drafts"}
            if app["is_public"] == 0:
                return {"status": 2, "message": "Team members are not open"}
            if app["status"] != 1:
                return {"status": 2, "message": "The app status is not normal"}
            
        encrypted_id = encrypt_id(app_id)
        app['api_url'] = f'/v1/app-api/{encrypted_id}/run-docs'

        conditions = [
            {"column": "app_id", "value": app_id},
            {"column": "team_id", "value": team_id},
            {"column": "publish_status", "value": publish_status},
            {"column": "status", "op": "in", "value": [1, 2]}
        ]

        # get workflow
        workflows = self.select_one(
            columns=["id AS workflows_id", "user_id", "app_id", "team_id", "graph", "features", "publish_status",
                     "published_time", "status"],
            conditions=conditions,
        )

        if not workflows:
            return {"status": 2, "message": "workflow error"}
        if workflows["user_id"] != uid and workflows["status"] != 1:
            return {"status": 2, "message": "The workflow status is not normal"}

        data = {
            "app": app,
            "workflow": workflows
        }

        return {"status": 1, "message": "success", "data": data}

    def get_workflows_list(self, page: int = 1, page_size: int = 10, uid: int = 0, team_id: int = 0,
                           workflows_search_type: int = 1, name: str = ""):

        if workflows_search_type == 1:
            conditions = [
                {"column": "workflows.user_id", "value": uid},
                {"column": "workflows.publish_status", "value": 0},
                {"column": "workflows.status", "op": "in", "value": [1, 2]},
                {"column": "apps.mode", "value": 2},
                {"column": "apps.status", "op": "in", "value": [1, 2]}
            ]
        elif workflows_search_type == 2:
            conditions = [
                {"column": "workflows.team_id", "value": team_id},
                {"column": "workflows.user_id", "op": "!=", "value": uid},
                {"column": "workflows.publish_status", "value": 1},
                {"column": "workflows.status", "value": 1},
                {"column": "apps.mode", "value": 2},
                {"column": "apps.is_public", "value": 1},
                {"column": "apps.status", "value": 1}
            ]
        else:
            conditions = [
                {"column": "workflows.user_id", "value": uid},
                {"column": "workflows.publish_status", "value": 1},
                {"column": "workflows.status", "value": 1},
                {"column": "apps.mode", "value": 2},
                {"column": "apps.status", "value": 1},
            ]
        if name:
            conditions.append({"column": "apps.name", "op": "like", "value": "%" + name + "%"})

        total_count = self.select(
            aggregates={"id": "count"},
            joins=[
                ["left", "apps", "workflows.app_id = apps.id"],
                ["left", "users", "workflows.user_id = users.id"]
            ],
            conditions=conditions,
        )[0]["count_id"]

        list = self.select(
            columns=[
                "workflows.id AS workflows_id", 
                "workflows.user_id", 
                "workflows.app_id", 
                "apps.publish_status", 
                "apps.name", 
                "apps.description", 
                "users.nickname", 
                "apps.avatar", 
                "apps.icon_background", "apps.avatar",
                "apps.icon"
                ],
            joins=[
                ["left", "apps", "workflows.app_id = apps.id"],
                ["left", "users", "workflows.user_id = users.id"]
            ],
            conditions=conditions,
            order_by="workflows.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        for item in list:
            # if item.get('avatar'):
            #     item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
            if item.get('avatar'):
                if not item['avatar'].startswith(('http://', 'https://')):
                    item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
            if item['publish_status'] == 1:
                workflow_info = self.select_one(
                    columns=["published_time"],
                    conditions=[
                        {"column": "app_id", "value": item['app_id']},
                        {"column": "publish_status", "value": 1}
                    ]
                )
                item['workflow_published_time'] = format_iso_time(workflow_info['published_time']) if workflow_info else None
        return {
            "list": list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }
        
    def get_draft_workflow(self, app_id: int, uid: int, team_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the draft workflow for a given app_id.
        
        Args:
            app_id (int): The ID of the app.
            uid (int): The ID of the user.
            team_id (int): The ID of the team.
            
        Returns:
            Optional[Dict[str, Any]]: The draft workflow if available, otherwise None.
        """
        return self.select_one(
            columns=["id", "graph", "features", "team_id", "user_id", "app_id", "status"],
            conditions=[
                {"column": "app_id", "value": app_id},
                {"column": "user_id", "value": uid},
                {"column": "team_id", "value": team_id},
                {"column": "status", "op": "<", "value": Workflows.del_status},
                {"column": "publish_status", "value": Workflows.w_publish_status}
            ]
        )

    def publish_workflows(self, app_id, uid, team_id):
        publish_info = self.select_one(columns=[
            'id',
            'graph',
            'features',
            'team_id',
            'user_id',
            'app_id',
            'status',
        ],
            conditions=[
                {'column': 'app_id', 'value': app_id},
                {'column': 'user_id', 'value': uid},
                {'column': 'team_id', 'value': team_id},
                {'column': 'status', 'op': '<', 'value': Workflows.del_status},
                {'column': 'publish_status', 'value': Workflows.publish_status},
            ])
        draft_info = self.get_draft_workflow(app_id, uid, team_id)
        if not publish_info and not draft_info:
            return False
        Apps().update_publish_status(app_id)
        if publish_info:
            if not draft_info:
                raise ValueError(get_language_content("no_available_workflows"))
            conditions = [{"column": "workflows.id", "value": publish_info['id']},
                          {"column": "workflows.user_id", "value": uid},
                          {"column": "workflows.team_id", "value": team_id}]
            res = self.update(conditions, {
                'publish_status': Workflows.publish_status,
                'published_time': datetime.now(),
                'graph': draft_info['graph'],
                'features': draft_info['features']
            })
            return res
        else:
            try:
                if not draft_info:
                    raise ValueError(get_language_content("no_available_workflows"))
                return self.insert({
                    'team_id': draft_info['team_id'],
                    'user_id': draft_info['user_id'],
                    'app_id': draft_info['app_id'],
                    'graph': draft_info['graph'],
                    'features': draft_info['features'],
                    'publish_status': Workflows.publish_status,
                    'published_time': datetime.now(),
                    'created_time': datetime.now(),
                    'updated_time': datetime.now(),
                    'status': draft_info['status']
                })
            except SQLAlchemyError as exc:
                return False

    def workflow_app_update(self, app_id: int = 0, uid: int = 0, is_public: int = 0, enable_api: int = 0,
                            graph: Dict[str, Any] = None):
        # verify app
        apps_model = Apps()
        app = apps_model.select_one(columns="*",
                                    conditions=[{"column": "id", "value": app_id}, {"column": "user_id", "value": uid},
                                                {"column": "mode", "value": 2},
                                                {"column": "status", "op": "in", "value": [1, 2]}])
        if not app:
            return {"status": 2, "message": "app error"}

        # verify workflow
        workflow = self.select_one(columns="*", conditions=[{"column": "app_id", "value": app_id},
                                                            {"column": "user_id", "value": uid},
                                                            {"column": "publish_status", "value": 0},
                                                            {"column": "status", "op": "in", "value": [1, 2]}])
        if not workflow:
            return {"status": 2, "message": "workflow error"}
        
        graph_changed = True
        if 'graph' in workflow and workflow['graph']:
            graph_changed = workflow['graph']['edges'] != graph['edges'] or workflow['graph']['nodes'] != graph['nodes']

        # get App(Agent Skill Dataset) ID
        app_id_list = self.get_node_appid(graph)
    
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # update app
            apps_data = {
                "is_public": is_public,
                "enable_api": enable_api,
                "updated_time": current_time
            }
            apps_update_res = apps_model.update({"column": "id", "value": workflow["app_id"]}, apps_data)
            if not apps_update_res:
                return {"status": 2, "message": "apps update error"}

            # update workflow
            workflow_data = {
                "graph": graph,
                # "features": features
            }
            workflow_update_result = self.update({"column": "id", "value": workflow['id']}, workflow_data)
            if not workflow_update_result:
                return {"status": 2, "message": "workflow update error"}

            # delete app_workflow_relation
            app_workflow_relation_model = AppWorkflowRelations()
            app_workflow_relation_model.delete({"column": "workflow_app_id", "value": app_id})

            # create app_workflow_relation
            if app_id_list and app_id_list != [0]:
                app_workflow_relation_model = AppWorkflowRelations()
                for asd_app_id in app_id_list:
                    app_workflow_relation_res = app_workflow_relation_model.insert(
                        {"app_id": asd_app_id, "workflow_id": workflow['id'], "workflow_app_id": app_id})
                    if not app_workflow_relation_res:
                        return {"status": 2, "message": "app workflow relation insert error"}


        except:
            return {"status": 2, "message": "workflow app update error"}

        return {"status": 1, "message": "success", "data": {'graph_changed': graph_changed}}

    def workflow_app_delete(self, app_id: int = 0, uid: int = 0):
        # verify app
        apps_model = Apps()
        app = apps_model.select_one(columns="*",
                                    conditions=[{"column": "id", "value": app_id}, {"column": "user_id", "value": uid},
                                                {"column": "mode", "value": 2},
                                                {"column": "status", "op": "in", "value": [1, 2]}])
        if not app:
            return {"status": 2, "message": "app error"}
        # verify workflow
        workflow = self.select(columns="*",
                               conditions=[{"column": "app_id", "value": app_id}, {"column": "user_id", "value": uid},
                                           {"column": "status", "op": "in", "value": [1, 2]}])

        if not workflow:
            return {"status": 2, "message": "workflow error"}
        try:

            # delete app
            delete_app_res = apps_model.soft_delete([{"column": "id", "value": app_id}])
            if not delete_app_res:
                return {"status": 2, "message": "delete app error"}

            for workflow_val in workflow:
                # delete agent
                delete_agent_res = self.soft_delete([{"column": "id", "value": workflow_val["id"]}])
                if not delete_agent_res:
                    return {"status": 2, "message": "delete agent error"}

                # delete agent dataset relation
                app_workflow_relation_model = AppWorkflowRelations()
                app_workflow_relation_model.delete({"column": "workflow_id", "value": workflow_val["id"]})
        except:
            return {"status": 2, "message": "workflow app delete error"}

        return {"status": 1, "message": "success", "data": {}}

    def get_workflow_log(self, page: int = 1, page_size: int = 10, app_id: int = 0, app_runs_name: str = "",
                         app_runs_status: int = 0, uid: int = 0):
        conditions = [
            {"column": "workflows.user_id", "value": uid},
            # {"column": "workflows.publish_status", "value": 1},
            {"column": "workflows.status", "op": "in", "value": [1, 2]},
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
                ["left", "apps", "workflows.app_id = apps.id"],
                ["left", "app_runs", "apps.id = app_runs.app_id"]
            ],
            conditions=conditions,
        )[0]["count_id"]

        list = self.select(
            columns=["workflows.id AS workflows_id", "workflows.user_id", "workflows.app_id",
                     "apps.name", "app_runs.id AS app_runs_id", "app_runs.name AS app_runs_name",
                     "app_runs.type AS app_runs_type",
                     "app_runs.level AS app_runs_level", "app_runs.created_time", "app_runs.updated_time",
                     "app_runs.elapsed_time", "app_runs.finished_time",
                     "app_runs.status AS app_runs_status", "app_runs.completed_steps", "app_runs.total_steps",
                     "app_runs.total_tokens",
                     "users.nickname"
                     ],
            joins=[
                ["left", "apps", "workflows.app_id = apps.id"],
                ["left", "app_runs", "apps.id = app_runs.app_id"],
                ["left", "users", "users.id = apps.user_id"]
            ],
            conditions=conditions,
            order_by="workflows.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        if list:
            for log in list:
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

    def node_run_info(self, app_id, node_id, uid, team_id):
        draft_info = self.select_one(columns=[
            'id',
            'graph',
            'features',
            'team_id',
            'user_id',
            'app_id',
            'status',
        ], conditions=[
            {'column': 'app_id', 'value': app_id},
            {'column': 'user_id', 'value': uid},
            {'column': 'team_id', 'value': team_id},
            {'column': 'status', 'op': '<', 'value': Workflows.del_status},
            {'column': 'publish_status', 'value': Workflows.w_publish_status},
        ])
        if not draft_info:
            raise ValueError(get_language_content('no_available_workflows'))

        graph = draft_info['graph']

        if not graph:
            raise ValueError(get_language_content('no_available_workflows'))

        return draft_info

    def get_node_appid(self, graph: Dict[str, Any]):
        """
            params:graph is a dictionary of data that contains the Agent Skill Dataset
            desc:get node app id

            return app_id array of Agent Skill Dataset
        """
        if graph:

            dataset_id_set = set()
            agent_id_set = set()
            skill_id_set = set()
            for node in graph.get('nodes', []):
                node_data = node.get('data', {})
                node_type = node_data.get('type')
                if node_type == 'agent':
                    agent_id = node_data.get('agent_id')
                    agent_id_set.add(agent_id)
                elif node_type == 'retriever':
                    datasets = node_data.get('datasets', [])
                    dataset_id_set.update(datasets)
                elif node_type == 'skill':
                    skill_id = node_data.get('skill_id')
                    skill_id_set.add(skill_id)

            agent_app_id = []
            datasets_app_id = []
            skill_app_id = []

            if agent_id_set:
                agent_model = Agents()
                agent_list = agent_model.select(columns="*",
                                                conditions=[{"column": "id", "op": "in", "value": sorted(agent_id_set)},
                                                            {"column": "publish_status", "value": 1},
                                                            {"column": "status", "op": "in", "value": [1, 2]}])
                if agent_list:
                    agent_app_id = [item['app_id'] for item in agent_list]
            if dataset_id_set:
                datasets_model = Datasets()
                datasets_list = datasets_model.select(columns="*", conditions=[
                    {"column": "id", "op": "in", "value": sorted(dataset_id_set)},
                    {"column": "status", "op": "in", "value": [1, 2]}])
                if datasets_list:
                    datasets_app_id = [item['app_id'] for item in datasets_list]

            if skill_id_set:
                skill_model = CustomTools()
                skill_list = skill_model.select(columns="*",
                                                conditions=[{"column": "id", "op": "in", "value": sorted(skill_id_set)},
                                                            {"column": "publish_status", "value": 1},
                                                            {"column": "status", "op": "in", "value": [1, 2]}])
                if skill_list:
                    skill_app_id = [item['app_id'] for item in skill_list]

            return agent_app_id + datasets_app_id + skill_app_id

    def workflow_info(self, app_id, run_type, team_id):
        publish_status = Workflows.w_publish_status if run_type == 1 else Workflows.publish_status
        publish_info = self.select_one(
            columns=[
                'id', 'team_id', 'user_id', 'app_id', 'graph', 'publish_status', 'published_time',
                'apps.name', 'apps.description', 'apps.enable_api', 'apps.is_public', 'apps.created_time',
                'apps.updated_time'
            ],
            joins=[('inner', 'apps', 'workflows.app_id = apps.id')],
            conditions=[
                {'column': 'app_id', 'value': app_id},
                {'column': 'team_id', 'value': team_id},
                {'column': 'status', 'value': 1},
                {'column': 'apps.status', 'value': 1},
                {'column': 'publish_status', 'value': publish_status},
            ]
        )
        if not publish_info:
            raise Exception("No available workflows by run_type")
        return publish_info

    def get_published_workflow(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Get the published workflow for a given app_id.
        
        Args:
            app_id (int): The ID of the app.
            
        Returns:
            Optional[Dict[str, Any]]: The published workflow if available, otherwise None.
        """
        workflows = self.select(
            columns=["app_id", "id AS workflow_id", "graph", "publish_status"],
            conditions=[
                {"column": "app_id", "value": app_id},
                {"column": "status", "op": "!=", "value": 3}
            ]
        )
        published_workflow = None
        draft_workflow = None
        for workflow in workflows:
            if workflow["publish_status"] == 1:
                published_workflow = workflow
                break
            elif workflow["publish_status"] == 0:
                draft_workflow = workflow
        if published_workflow:
            return published_workflow
        else:
            return draft_workflow
