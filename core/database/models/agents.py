from typing import Any, Dict, List
from core.database import MySQL
from core.database.models.datasets import Datasets
from core.database.models.apps import Apps
from core.database.models.agent_dataset_relation import AgentDatasetRelation
from core.database.models.agent_abilities import AgentAbilities
from core.database.models.model_configurations import ModelConfigurations
from core.database.models.chatroom_agent_relation import ChatroomAgentRelation
from core.database.models.agent_callable_items import AgentCallableItems
from core.database.models.tag_bindings import TagBindings
from core.database.models.users import Users
from datetime import datetime
from core.helper import generate_api_token, encrypt_id
from languages import get_language_content
import math
from config import settings


class Agents(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "agents"
    """
    Indicates whether the `agents` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_agent_by_id(self, agent_id: int, user_id: int = 0) -> Dict[str, Any]:
        """
        Retrieves an agent record from the {table_name} table based on the specified agent ID.

        :param agent_id: An integer representing the agent ID.
        :return: A dictionary representing the agent record.
        """
        agent = self.select_one(
            columns=[
                "agents.id",
                "apps.name",
                "apps.description",
                "agents.app_id",
                "agents.obligations",
                "agents.input_variables",
                "agents.auto_match_ability",
                "agents.default_output_format",
                "agents.model_config_id",
                "agents.allow_upload_file",
                "agents.publish_status"
            ],
            joins=[["inner", "apps", "agents.app_id = apps.id"]],
            conditions=[
                {"column": "id", "value": agent_id},
                {"column": "status", "value": 1}
            ]
        )
        assert agent, get_language_content('agent_does_not_exist', user_id)
        return agent

    def get_agent_list(self, page: int = 1, page_size: int = 10, uid: int = 0, team_id: int = 0,
                       agent_search_type: int = 1, name: str = ""):
        """
        Obtain agent list data based on parameters

        :param page: Page number.
        :param page_size: Quantity per page.
        :param uid: User ID.
        :param team_id: Team ID.
        :param agent_search_type: Agent search type 1: my agent 2: team agent 3: select my agent.
        :param name: App and agent name.
        :return: A dictionary representing the agent list record.
        """
        if agent_search_type == 1:
            conditions = [
                {"column": "agents.user_id", "value": uid},
                {"column": "agents.publish_status", "value": 0},
                {"column": "agents.status", "op": "in", "value": [1, 2]},
                {"column": "apps.mode", "value": 1},
                {"column": "apps.status", "op": "in", "value": [1, 2]}
            ]
        elif agent_search_type == 2:
            conditions = [
                {"column": "agents.team_id", "value": team_id},
                {"column": "agents.user_id", "op": "!=", "value": uid},
                {"column": "agents.publish_status", "value": 1},
                {"column": "agents.status", "value": 1},
                {"column": "apps.mode", "value": 1},
                {"column": "apps.is_public", "value": 1},
                {"column": "apps.status", "value": 1}
            ]
        else:
            conditions = [
                {"column": "agents.user_id", "value": uid},
                {"column": "agents.publish_status", "value": 1},
                {"column": "agents.status", "value": 1},
                {"column": "apps.mode", "value": 1},
                {"column": "apps.status", "value": 1},
            ]
        if name:
            conditions.append({"column": "apps.name", "op": "like", "value": "%" + name + "%"})

        total_count = self.select(
            aggregates={"id": "count"},
            joins=[
                ["left", "apps", "agents.app_id = apps.id"],
                ["left", "users", "agents.user_id = users.id"]
            ],
            conditions=conditions,
        )[0]["count_id"]

        list = self.select(
            columns=["agents.id AS agent_id", "agents.app_id", "apps.name", "apps.description", "apps.icon", "apps.avatar",
                     "apps.icon_background", "users.nickname", "users.avatar"],
            joins=[
                ["left", "apps", "agents.app_id = apps.id"],
                ["left", "users", "agents.user_id = users.id"]
            ],
            conditions=conditions,
            order_by="agents.id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        if list:
            for item in list:
                if item.get('avatar'):
                    item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

        return {
            "list": list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def agent_base_update(self, agent_id: int, uid: int = 0, team_id: int = 0, is_public: int = 0, enable_api: int = 0,
                          obligations: str = "", input_variables: Dict[str, Any] = None, dataset_ids: List[int] = None,
                          m_config_id: int = 0, allow_upload_file: int = 0, default_output_format: int = 1, attrs_are_visible: int = 0):
        """
        Update base agent data based on parameters

        :param agent_id: Agent id.
        :param uid: User ID.
        :param team_id: Team ID.
        :param is_public: Is it open to team members? 0: No 1: Yes.
        :param attrs_are_visible: Are attributes of this app visible? 0: No 1: Yes.
        :param enable_api: Whether to enable API 0: No 1: Yes.
        :param obligations: Agent obligations.
        :param input_variables: Input variables.
        :param dataset_ids: Multiple dataset id.
        :param m_config_id: Model configuration ID.
        :param allow_upload_file: Is it allowed to upload files? 0: No 1: Yes.
        :param default_output_format: Default output format 1: text 2: json 3: code.
        :return: A dictionary representing the result record.
        """
        # verify agent
        agent = self.select_one(columns="*",
                                conditions=[{"column": "id", "value": agent_id}, {"column": "user_id", "value": uid},
                                            {"column": "publish_status", "value": 0},
                                            {"column": "status", "op": "in", "value": [1, 2]}])
        if not agent:
            return {"status": 2, "message": get_language_content("api_agent_base_update_agent_error")}

        # verify dataset data
        if dataset_ids and dataset_ids != [0]:
            datasets_model = Datasets()
            datasets = datasets_model.select(
                columns=["datasets.id AS dataset_id", "datasets.app_id", "apps.name"],
                joins=[
                    ["left", "apps", "datasets.app_id = apps.id"]
                ],
                conditions=[
                    {"column": "datasets.id", "op": "in", "value": dataset_ids},
                    {"column": "datasets.team_id", "value": team_id},
                    {"column": "datasets.status", "value": 1},
                    {"column": "apps.mode", "value": 3},
                    {"column": "apps.status", "value": 1}
                ]
            )
            if len(datasets) != len(dataset_ids):
                return {"status": 2, "message": get_language_content("api_agent_base_update_datasets_error")}

        # verify model config
        model_configurations_model = ModelConfigurations()
        model_configuration = model_configurations_model.select_one(
            columns=["model_configurations.id AS m_config_id", "model_configurations.model_id AS m_id",
                     "models.name AS m_name", "models.supplier_id", "suppliers.name AS supplier_name"],
            joins=[
                ["left", "models", "model_configurations.model_id = models.id"],
                ["left", "suppliers", "models.supplier_id = suppliers.id"]
            ],
            conditions=[
                {"column": "model_configurations.id", "value": m_config_id},
                {"column": "model_configurations.team_id", "value": team_id},
                {"column": "model_configurations.status", "value": 1},
                {"column": "models.type", "value": 1},
                {"column": "models.status", "value": 1},
                {"column": "suppliers.status", "value": 1}
            ]
        )
        if not model_configuration:
            return {"status": 2, "message": get_language_content("api_agent_base_update_model_configuration_error")}

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # update app
            apps_data = {
                "is_public": is_public,
                "attrs_are_visible": attrs_are_visible,
                "enable_api": enable_api,
                "updated_time": current_time
            }
            apps_model = Apps()
            apps_update_res = apps_model.update({"column": "id", "value": agent["app_id"]}, apps_data)
            if not apps_update_res:
                return {"status": 2, "message": get_language_content("api_agent_base_update_apps_update_error")}

            # update agent
            agents_data = {
                "obligations": obligations,
                "input_variables": input_variables,
                "model_config_id": m_config_id,
                "allow_upload_file": allow_upload_file,
                "default_output_format": default_output_format,
                "updated_time": current_time
            }
            agent_update_res = self.update({"column": "id", "value": agent_id}, agents_data)
            if not agent_update_res:
                return {"status": 2, "message": get_language_content("api_agent_base_update_agents_update_error")}

            # delete agent dataset relation
            agent_dataset_relation_model = AgentDatasetRelation()
            agent_dataset_relation_model.delete({"column": "agent_id", "value": agent_id})

            # create agent dataset relation
            if dataset_ids and dataset_ids != [0]:
                for dataset_id in dataset_ids:
                    res = agent_dataset_relation_model.insert({"agent_id": agent_id, "dataset_id": dataset_id})
                    if not res:
                        return {"status": 2,
                                "message": get_language_content("api_agent_base_update_agent_dataset_insert_error")}
        except:
            return {"status": 2, "message": get_language_content("api_agent_base_update_agent_base_update_error")}

        return {"status": 1, "message": get_language_content("api_agent_success"),
                "data": {"app_id": agent["app_id"], "agent_id": agent_id}}

    def agent_abilities_set(self, agent_id: int, uid: int, auto_match_ability: int, agent_abilities: List):
        """
        Set agent abilities based on parameters

        :param agent_id: Agent id.
        :param uid: User ID.
        :param auto_match_ability: Whether to automatically match abilities 0: No 1: Yes.
        :param agent_abilities: Agent abilities list.
        :return: A dictionary representing the result record.
        """
        # verify agent
        agent = self.select_one(columns="*",
                                conditions=[{"column": "id", "value": agent_id}, {"column": "user_id", "value": uid},
                                            {"column": "publish_status", "value": 0},
                                            {"column": "status", "op": "in", "value": [1, 2]}])
        if not agent:
            return {"status": 2, "message": get_language_content("api_agent_abilities_set_agent_error")}

        update_abilities_ids = []
        if agent_abilities:
            for abilities_val in agent_abilities:
                if abilities_val.agent_ability_id > 0:
                    update_abilities_ids.append(abilities_val.agent_ability_id)
                if not abilities_val.name:
                    return {"status": 2,
                            "message": get_language_content("api_agent_abilities_set_abilities_name_required")}
                if not abilities_val.content:
                    return {"status": 2,
                            "message": get_language_content("api_agent_abilities_set_abilities_content_required")}
                if abilities_val.status not in [1, 2]:
                    return {"status": 2,
                            "message": get_language_content("api_agent_abilities_set_abilities_status_error")}
                if abilities_val.output_format not in [0, 1, 2, 3]:
                    return {"status": 2, "message": get_language_content("api_agent_abilities_set_output_format_error")}

        agent_abilities_model = AgentAbilities()
        if update_abilities_ids:
            update_agent_abilities = agent_abilities_model.select(
                columns="*",
                conditions=[
                    {"column": "id", "op": "in", "value": update_abilities_ids},
                    {"column": "user_id", "value": uid},
                    {"column": "agent_id", "value": agent_id},
                    {"column": "status", "op": "in", "value": [1, 2]}
                ]
            )
            if len(update_agent_abilities) != len(update_abilities_ids):
                return {"status": 2, "message": get_language_content("api_agent_abilities_set_agent_abilities_error")}

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # update agent
            agents_data = {
                "auto_match_ability": auto_match_ability,
                "updated_time": current_time
            }
            agent_update_res = self.update({"column": "id", "value": agent_id}, agents_data)
            if not agent_update_res:
                return {"status": 2, "message": get_language_content("api_agent_abilities_set_agents_update_error")}

            # delete abilities
            delete_abilities_conditions = [
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
            if update_abilities_ids:
                delete_abilities_conditions.append({"column": "id", "op": "not in", "value": update_abilities_ids})
            agent_abilities_model.soft_delete(delete_abilities_conditions)

            # create or update abilities
            if agent_abilities:
                for abilities_value in agent_abilities:
                    if abilities_value.agent_ability_id > 0:
                        # update abilities
                        update_abilities_data = {
                            "name": abilities_value.name,
                            "content": abilities_value.content,
                            "updated_time": current_time,
                            "status": abilities_value.status,
                            "output_format": abilities_value.output_format
                        }
                        update_abilities_res = agent_abilities_model.update(
                            {"column": "id", "value": abilities_value.agent_ability_id}, update_abilities_data)
                        if not update_abilities_res:
                            return {"status": 2,
                                    "message": get_language_content("api_agent_abilities_set_abilities_update_error")}
                    else:
                        # create abilities
                        create_abilities_data = {
                            "user_id": uid,
                            "agent_id": agent_id,
                            "name": abilities_value.name,
                            "content": abilities_value.content,
                            "created_time": current_time,
                            "updated_time": current_time,
                            "status": abilities_value.status,
                            "output_format": abilities_value.output_format
                        }
                        create_abilities_res = agent_abilities_model.insert(create_abilities_data)
                        if not create_abilities_res:
                            return {"status": 2,
                                    "message": get_language_content("api_agent_abilities_set_abilities_insert_error")}
        except:
            return {"status": 2, "message": get_language_content("api_agent_abilities_set_agent_abilities_set_error")}

        return {"status": 1, "message": get_language_content("api_agent_success"), "data": {}}

    def agent_publish(self, agent_id: int, uid: int):
        """
        Publish agent based on parameters

        :param agent_id: Agent id.
        :param uid: User ID.
        :return: A dictionary representing the result record.
        """
        # verify agent
        agent = self.select_one(columns="*",
                                conditions=[{"column": "id", "value": agent_id}, {"column": "user_id", "value": uid},
                                            {"column": "publish_status", "value": 0},
                                            {"column": "status", "op": "in", "value": [1, 2]}])
        if not agent:
            return {"status": 2, "message": get_language_content("api_agent_publish_agent_error")}

        # verify app
        apps_model = Apps()
        app = apps_model.select_one(columns="*", conditions=[{"column": "id", "value": agent["app_id"]},
                                                             {"column": "user_id", "value": uid},
                                                             {"column": "mode", "value": 1},
                                                             {"column": "status", "op": "in", "value": [1, 2]}])
        if not app:
            return {"status": 2, "message": get_language_content("api_agent_publish_app_error")}

        agent_dataset_relation_model = AgentDatasetRelation()
        agent_dataset_relation_list = agent_dataset_relation_model.select(
            columns="*",
            conditions=[
                {"column": "agent_id", "value": agent_id},
            ]
        )

        agent_abilities_model = AgentAbilities()
        agent_abilities_list = agent_abilities_model.select(
            columns="*",
            conditions=[
                {"column": "agent_id", "value": agent_id},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        
        agent_callable_items_model = AgentCallableItems()
        agent_callable_items_list = agent_callable_items_model.select(
            columns="*",
            conditions=[
                {"column": "agent_id", "value": agent_id}
            ]
        )

        published_agent = self.select_one(columns="*", conditions=[{"column": "app_id", "value": agent["app_id"]},
                                                                   {"column": "publish_status", "value": 1},
                                                                   {"column": "status", "op": "in", "value": [1, 2]}])

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # create or update publish agent
            agents_data = {
                "team_id": agent["team_id"],
                "user_id": agent["user_id"],
                "app_id": agent["app_id"],
                "obligations": agent["obligations"],
                "input_variables": agent["input_variables"],
                "auto_match_ability": agent["auto_match_ability"],
                "default_output_format": agent["default_output_format"],
                "model_config_id": agent["model_config_id"],
                "allow_upload_file": agent["allow_upload_file"],
                "publish_status": 1,
                "published_time": current_time,
                "updated_time": current_time,
                "status": agent["status"],
            }
            if published_agent:
                # update publish agent
                published_agent_id = published_agent["id"]
                agent_update_res = self.update({"column": "id", "value": published_agent_id}, agents_data)
                if not agent_update_res:
                    return {"status": 2, "message": get_language_content("api_agent_publish_agent_update_error")}

                # delete publish agent dataset relation
                agent_dataset_relation_model.delete({"column": "agent_id", "value": published_agent_id})

                # delete publish abilities
                agent_abilities_model.soft_delete([{"column": "agent_id", "value": published_agent_id},
                                                   {"column": "status", "op": "in", "value": [1, 2]}])
                agent_callable_items_model.delete([{"column": "agent_id", "value": published_agent_id}])
            else:
                # create publish agent
                agents_data["created_time"] = current_time
                published_agent_id = self.insert(agents_data)
                if not published_agent_id:
                    return {"status": 2, "message": get_language_content("api_agent_publish_agent_insert_error")}

            # create agent dataset relation
            if agent_dataset_relation_list:
                for dataset_relation_val in agent_dataset_relation_list:
                    insert_relation_res = agent_dataset_relation_model.insert(
                        {"agent_id": published_agent_id, "dataset_id": dataset_relation_val["dataset_id"]})
                    if not insert_relation_res:
                        return {"status": 2,
                                "message": get_language_content("api_agent_publish_agent_dataset_insert_error")}

            # create abilities
            if agent_abilities_list:
                for agent_abilities_val in agent_abilities_list:
                    create_abilities_data = {
                        "user_id": agent_abilities_val["user_id"],
                        "agent_id": published_agent_id,
                        "name": agent_abilities_val["name"],
                        "content": agent_abilities_val["content"],
                        "output_format": agent_abilities_val["output_format"],
                        "status": agent_abilities_val["status"],
                        "created_time": current_time,
                        "updated_time": current_time
                    }
                    create_abilities_res = agent_abilities_model.insert(create_abilities_data)
                    if not create_abilities_res:
                        return {"status": 2,
                                "message": get_language_content("api_agent_publish_abilities_insert_error")}
            
            if agent_callable_items_list:
                for agent_callable_items_val in agent_callable_items_list:
                    create_callable_items_data = {
                        "agent_id": published_agent_id,
                        "app_id": agent_callable_items_val["app_id"],
                        "item_type": agent_callable_items_val["item_type"],
                        "created_time": current_time,
                        "updated_time": current_time
                    }
                    create_callable_items_res = agent_callable_items_model.insert(create_callable_items_data)
                    if not create_callable_items_res:
                        return {"status": 2,
                                "message": get_language_content("api_agent_callable_items_insert_error")}
            # update publish app
            app_data = {
                "publish_status": 1,
                "updated_time": current_time
            }
            # Generate a token when the token is empty
            if not app["api_token"]:
                app_data["api_token"] = generate_api_token()
            apps_update_res = apps_model.update({"column": "id", "value": agent["app_id"]}, app_data)
            if not apps_update_res:
                return {"status": 2, "message": get_language_content("api_agent_publish_app_update_error")}
        except:
            return {"status": 2, "message": get_language_content("api_agent_publish_agent_publish_error")}

        return {"status": 1, "message": get_language_content("api_agent_success"),
                "data": {"app_id": app["id"], "enable_api": app["enable_api"]}}

    def agent_delete(self, app_id: int, uid: int):
        """
        Delete agent based on parameters

        :param app_id: App id.
        :param uid: User ID.
        :return: A dictionary representing the result record.
        """
        from core.database.models.chatrooms import Chatrooms

        # verify app
        apps_model = Apps()
        app = apps_model.select_one(columns="*",
                                    conditions=[{"column": "id", "value": app_id}, {"column": "user_id", "value": uid},
                                                {"column": "mode", "value": 1},
                                                {"column": "status", "op": "in", "value": [1, 2]}])
        if not app:
            return {"status": 2, "message": get_language_content("api_agent_delete_app_error")}

        # verify agent
        agents = self.select(columns="*",
                             conditions=[{"column": "app_id", "value": app_id}, {"column": "user_id", "value": uid},
                                         {"column": "status", "op": "in", "value": [1, 2]}])
        if not agents:
            return {"status": 2, "message": get_language_content("api_agent_delete_agent_error")}

        try:
            # delete app
            delete_app_res = apps_model.soft_delete([{"column": "id", "value": app_id}])
            if not delete_app_res:
                return {"status": 2, "message": get_language_content("api_agent_delete_delete_app_error")}

            for agent_val in agents:
                # delete agent
                delete_agent_res = self.soft_delete([{"column": "id", "value": agent_val["id"]}])
                if not delete_agent_res:
                    return {"status": 2, "message": get_language_content("api_agent_delete_delete_agent_error")}

                # delete agent dataset relation
                agent_dataset_relation_model = AgentDatasetRelation()
                agent_dataset_relation_model.delete({"column": "agent_id", "value": agent_val["id"]})

                # delete abilities
                agent_abilities_model = AgentAbilities()
                agent_abilities_model.soft_delete([{"column": "agent_id", "value": agent_val["id"]},
                                                   {"column": "status", "op": "in", "value": [1, 2]}])

                # delete chatroom agent relation
                chatroom_agent_relation_model = ChatroomAgentRelation()
                chatroom_agent_relation_model.delete({"column": "agent_id", "value": agent_val["id"]})

                # delete agent chatrooms
                agent_chatrooms = Chatrooms().select(
                    columns=["id", "app_id"],
                    conditions=[
                        {"column": "chat_agent_id", "value": agent_val["id"]},
                        {"column": "status", "value": 1}
                    ]
                )
                for agent_chatroom in agent_chatrooms:
                    Chatrooms().update(
                        {"column": "id", "value": agent_chatroom["id"]},
                        {"status": 3}
                    )
                    Apps().update(
                        {"column": "id", "value": agent_chatroom["app_id"]},
                        {"status": 3}
                    )
                    ChatroomAgentRelation().delete(
                        {"column": "chatroom_id", "value": agent_chatroom["id"]}
                    )
        except:
            return {"status": 2, "message": get_language_content("api_agent_delete_agent_delete_error")}

        return {"status": 1, "message": get_language_content("api_agent_success"), "data": {}}

    def _get_agent_chatroom_id(self, agent_id: int, user_id: int, team_id: int) -> int:
        from core.database.models.chatrooms import Chatrooms

        chatroom_info = Chatrooms().select_one(
            columns=['id'],
            conditions=[
                {'column': 'team_id', 'value': team_id},
                {'column': 'user_id', 'value': user_id},
                {'column': 'chat_agent_id', 'value': agent_id},
                {'column': 'status', 'value': 1}
            ]
        )
        if chatroom_info:
            return chatroom_info['id']
        else:
            # Create a new chatroom
            app_id = Apps().insert(
                {
                    'team_id': team_id,
                    'user_id': user_id,
                    'name': f'Agent Chat {user_id}-{agent_id}',
                    'description': f'Agent Chat for user {user_id} and agent {agent_id}',
                    'is_public': 0,
                    'mode': 5,  # Chatroom
                    'status': 1
                }
            )
            chatroom_id = Chatrooms().insert(
                {
                    'team_id': team_id,
                    'user_id': user_id,
                    'app_id': app_id,
                    'chat_agent_id': agent_id,
                    'is_temporary': 0,
                    'max_round': 10
                }
            )
            ChatroomAgentRelation().insert_agent(
                {
                    'chatroom_id': chatroom_id,
                    'agent': [{'agent_id': agent_id, 'active': 1}]
                }
            )
            return chatroom_id

    def agent_info(self, app_id: int, publish_status: int, uid: int, team_id: int):
        """
        Obtain agent info data based on parameters

        :param app_id: App ID.
        :param publish_status: Agent publish status 0: Draft 1: Published.
        :param uid: User ID.
        :param team_id: Team ID.
        :return: A dictionary representing the agent info record.
        """
        # get app
        
        from core.database.models.chatrooms import Chatrooms
        apps_model = Apps()
        app = apps_model.select_one(
            columns=["id AS app_id", "user_id", "name", "description", "icon", "icon_background", "is_public", "attrs_are_visible",
                     "publish_status", "api_token", "enable_api", "created_time", "status"],
            conditions=[
                {"column": "id", "value": app_id},
                {"column": "team_id", "value": team_id},
                {"column": "mode", "value": 1},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not app:
            return {"status": 2, "message": get_language_content("api_agent_info_app_error")}
        if app["user_id"] != uid:
            if publish_status == 0:
                return {"status": 2, "message": get_language_content("api_agent_info_not_creators")}
            if app["is_public"] == 0:
                return {"status": 2, "message": get_language_content("api_agent_info_team_not_open")}
            if app["status"] != 1:
                return {"status": 2, "message": get_language_content("api_agent_info_app_status_not_normal")}
        # Generate api_url
        encrypted_id = encrypt_id(app_id)
        app["api_url"] = f'/v1/app-api/{encrypted_id}/run-docs'

        # get agent
        agent = self.select_one(
            columns=["id AS agent_id", "user_id", "obligations", "input_variables", "auto_match_ability",
                     "default_output_format", "model_config_id AS m_config_id", "allow_upload_file", "publish_status",
                     "published_time", "created_time", "status"],
            conditions=[
                {"column": "app_id", "value": app_id},
                {"column": "team_id", "value": team_id},
                {"column": "publish_status", "value": publish_status},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )
        if not agent:
            return {"status": 2, "message": get_language_content("api_agent_info_agent_error")}
        if agent["user_id"] != uid and agent["status"] != 1:
            return {"status": 2, "message": get_language_content("api_agent_info_agent_status_not_normal")}

        # get agent dataset relation
        agent_dataset_relation_model = AgentDatasetRelation()
        agent_dataset_relation_list = agent_dataset_relation_model.select(
            columns=["agent_dataset_relation.dataset_id", "datasets.app_id", "apps.name"],
            joins=[
                ["left", "datasets", "agent_dataset_relation.dataset_id = datasets.id"],
                ["left", "apps", "datasets.app_id = apps.id"]
            ],
            conditions=[
                {"column": "agent_dataset_relation.agent_id", "value": agent["agent_id"]},
                {"column": "datasets.status", "value": 1},
                {"column": "apps.mode", "value": 3},
                {"column": "apps.status", "value": 1}
            ]
        )

        # get agent abilities
        agent_abilities_model = AgentAbilities()
        agent_abilities_list = agent_abilities_model.select(
            columns=["id AS agent_ability_id", "name", "content", "output_format", "status"],
            conditions=[
                {"column": "agent_id", "value": agent["agent_id"]},
                {"column": "status", "op": "in", "value": [1, 2]}
            ]
        )

        # get model configurations
        model_configurations_model = ModelConfigurations()
        m_configurations_list = model_configurations_model.select(
            columns=["model_configurations.id AS m_config_id", "model_configurations.model_id AS m_id",
                     "models.name AS m_name", "models.supplier_id", "suppliers.name AS supplier_name"],
            joins=[
                ["left", "models", "model_configurations.model_id = models.id"],
                ["left", "suppliers", "models.supplier_id = suppliers.id"]
            ],
            conditions=[
                {"column": "model_configurations.team_id", "value": team_id},
                {"column": "model_configurations.status", "value": 1},
                {"column": "models.type", "value": 1},
                {"column": "models.status", "value": 1},
                {"column": "suppliers.status", "value": 1}
            ],
            order_by="model_configurations.id ASC"
        )

        
        callable_items = AgentCallableItems().get_callable_items_by_agent_id(agent["agent_id"])

        # get user
        users_model = Users()
        user = users_model.select_one(
            columns=["id AS user_id", "nickname"],
            conditions=[
                {"column": "id", "value": app["user_id"]}
            ]
        )

        agent_chatroom_id = self._get_agent_chatroom_id(agent["agent_id"], uid, team_id)
        chat_status = Chatrooms().select_one(
            columns=["chat_status"],
            conditions=[
                {"column": "chat_agent_id", "value": agent["agent_id"]},
            ]
        )['chat_status']

        if app["user_id"] != uid and app["attrs_are_visible"] != 1:
            input_variables = {
                "agent_id": agent['agent_id'],
                "input_variables": agent['input_variables']
            }

            data = {
                "app": app,
                "agent": input_variables,
                "agent_chatroom_id": agent_chatroom_id,
                "callable_items": callable_items,
                "agent_dataset_relation_list": '',
                "agent_abilities_list": '',
                "m_configurations_list": '',
                "is_creator": 0 if app["user_id"] != uid else 1,
                "creator_nickname": user["nickname"] if user else None,
                "chat_status": chat_status
            }
        else:
            data = {
                "app": app,
                "agent": agent,
                "agent_chatroom_id": agent_chatroom_id,
                "callable_items": callable_items,
                "agent_dataset_relation_list": agent_dataset_relation_list,
                "agent_abilities_list": agent_abilities_list,
                "m_configurations_list": m_configurations_list,
                "is_creator": 0 if app["user_id"] != uid else 1,
                "creator_nickname": user["nickname"] if user else None,
                "chat_status": chat_status
            }

        return {"status": 1, "message": get_language_content("api_agent_success"), "data": data}

    def create_agent_with_configs(self, data: dict, user_id: int, team_id: int) -> dict:
        """
        Create new agent or update existing one with complete configurations.

        Args:
            data (dict): Complete agent configuration data containing:
                app_id (int, optional): If provided, updates existing agent
                name (str): Agent name
                description (str): Agent description 
                obligations (str): Agent obligations/responsibilities
                abilities (list): List of abilities configs
                tags (list, optional): List of tag IDs
            user_id (int): Current user ID
            team_id (int): Current team ID

        Returns:
            dict: Contains:
                status (int): 1 for success, 2 for failure
                message (str): Success/error message
                app_id (int): Created/updated app ID if successful
        """
        app_id = data.get("app_id", None)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            app_model = Apps()
            if app_id:
                # Update existing app
                base_data = {
                    "name": data["name"],
                    "description": data["description"],
                    "updated_time": current_time
                }

                # Verify app exists and belongs to user in this team
                existing_app = app_model.select_one(
                    columns=["id"],
                    conditions=[
                        {"column": "id", "value": app_id},
                        {"column": "team_id", "value": team_id},
                        {"column": "user_id", "value": user_id},
                        {"column": "status", "op": "in", "value": [1, 2]}
                    ]
                )
                if not existing_app:
                    return {"status": 2, "message": get_language_content("api_agent_info_app_error")}

                # Update app
                if not app_model.update({"column": "id", "value": app_id}, base_data):
                    return {"status": 2, "message": get_language_content("apps_update_error")}

                # Get associated agent
                agent = self.select_one(
                    columns=["id"],
                    conditions=[
                        {"column": "app_id", "value": app_id},
                        {"column": "team_id", "value": team_id},
                        {"column": "user_id", "value": user_id}
                    ]
                )
                if not agent:
                    return {"status": 2, "message": get_language_content("api_agent_info_agent_error")}

                agent_id = agent["id"]
                agent_config = {
                    "obligations": data["obligations"],
                    "team_id": team_id,
                    "updated_time": current_time
                }
                if not self.update({"column": "id", "value": agent_id}, agent_config):
                    return {"status": 2, "message": get_language_content("agents_update_error")}

                # Delete existing abilities (hard delete)
                agent_abilities_model = AgentAbilities()
                agent_abilities_model.delete([{"column": "agent_id", "value": agent["id"]}])
            else:
                # Create new app
                base_data = {
                    "name": data["name"],
                    "description": data["description"],
                    "mode": 1,
                    "publish_status": 0,
                    "team_id": team_id,
                    "user_id": user_id,
                    "created_time": current_time,
                    "updated_time": current_time
                }

                app_id = app_model.insert(base_data)
                if not app_id:
                    return {"status": 2, "message": get_language_content("apps_insert_error")}

                # Handle tags
                if data.get("tags", []):
                    tag_bindings = TagBindings()
                    if not tag_bindings.batch_update_bindings([app_id], data.get("tags", [])):
                        return {"status": 2, "message": get_language_content("tag_binding_create_failed")}

                # Create initial agent record
                agent_data = {
                    "team_id": team_id,
                    "user_id": user_id,
                    "app_id": app_id,
                    "created_time": current_time,
                    "updated_time": current_time
                }
                agent_id = self.insert(agent_data)
                if not agent_id:
                    return {"status": 2, "message": get_language_content("agents_insert_error")}

                # Update agent configurations
                model_id = ModelConfigurations().get_models_default_used_by_id(team_id=team_id, _type=1)
                if not model_id:
                    return {"status": 2,
                            "message": get_language_content("api_agent_base_update_model_configuration_error")}

                agent_config = {
                    "input_variables": {"name": "input", "type": "object", "properties": {
                        "default_var": {"name": "default_var", "type": "string", "value": "",
                                        "display_name": "Default variable", "required": 0, "max_length": 0}},
                                        "display_name": "", "to_string_keys": ""},
                    "obligations": data["obligations"],
                    'm_config_id': model_id
                }

                base_update_result = self.agent_base_update(
                    agent_id=agent_id,
                    uid=user_id,
                    team_id=team_id,
                    **agent_config
                )
                if base_update_result["status"] != 1:
                    return base_update_result

            # Set agent abilities
            from api.schema.agent import AgentAbilitiesData
            agent_abilities = [
                AgentAbilitiesData(
                    agent_ability_id=0,
                    name=ability["name"],
                    content=ability["content"],
                    status=1,
                    output_format=ability.get("output_format", 0)
                ) for ability in data["abilities"]
            ]
            ability_result = self.agent_abilities_set(
                agent_id=agent_id,
                uid=user_id,
                auto_match_ability=1,
                agent_abilities=agent_abilities
            )
            if ability_result["status"] != 1:
                return ability_result

            result = self.agent_publish(agent_id, user_id)
            if result["status"] != 1:
                return {"status": 2, "message": result["message"]}

            return {"status": 1, "message": get_language_content("api_agent_success"), "app_id": app_id}
        except Exception as e:
            return {"status": 2, "message": get_language_content("api_agent_create_error")}

    def get_agent_by_id_info(self, agent_id: int, user_id: int = 0) -> Dict[str, Any]:
        """
        Retrieves an agent record from the {table_name} table based on the specified agent ID.

        :param agent_id: An integer representing the agent ID.
        :param user_id: An integer representing the user ID.
        :return: A dictionary representing the agent record.
        """
        agent_info = self.select_one(
            columns=[
                "agents.id",
                "apps.name",
                "apps.description",
                "agents.app_id",
                "agents.obligations",
                "agents.input_variables",
                "agents.auto_match_ability",
                "agents.default_output_format",
                "agents.model_config_id",
                "agents.allow_upload_file",
                "agents.publish_status"
            ],
            joins=[["inner", "apps", "agents.app_id = apps.id"]],
            conditions=[
                {"column": "id", "value": agent_id},
                {"column": "status", "value": 1}
            ]
        )
        return agent_info

    def get_app_by_id_agent_info(self, app_id: int, user_id: int = 0):
        """
        Retrieves an agent record from the {table_name} table based on the specified agent ID.

        :param app_id: An integer representing the app ID.
        :param user_id: An integer representing the user ID.
        :return: A dictionary representing the agent record.
        """
        agent_info = self.select(
            columns=[
                "agents.id"
            ],
            joins=[["inner", "apps", "agents.app_id = apps.id"]],
            conditions=[
                {"column": "agents.app_id", "value": app_id},
                {"column": "agents.status", "value": 1}
            ]
        )

        agent_ids = []

        for agent in agent_info:
            agent_ids.append(agent["id"])

        return agent_ids

