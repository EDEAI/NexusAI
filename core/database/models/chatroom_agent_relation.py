from typing import Any, Dict
from core.database import MySQL
import math
from config import settings

class ChatroomAgentRelation(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "chatroom_agent_relation"
    """
    Indicates whether the `chatroom_agent_relation` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def get_agents_by_chatroom_id(self, chatroom_id: int):
        """
        Retrieves a list of agents associated with a specific chat room.

        This function queries the database to find all agents that are linked to the given chat room ID.
        It returns a list of dictionaries, where each dictionary contains the agent's ID, chat room ID, active status, and other relevant information.

        Parameters:
        - chatroom_id (int): The unique identifier of the chat room for which to retrieve agents. Required.

        Returns:
        - list: A list of dictionaries, each representing an agent associated with the chat room.
               Each dictionary contains the keys 'id', 'chatroom_id', 'agent_id', and 'active'.
        """
        info = self.select(
            columns=[
                'id', 'chatroom_id', 'agent_id', 'active',
            ],
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
            ]
        )
        return info

    def get_active_agents_by_chatroom_id(self, chatroom_id: int):
        """
        Retrieves a list of active agents associated with a specific chat room.

        This function queries the database to find all active agents that are linked to the given chat room ID.
        It returns a list of dictionaries, where each dictionary contains the agent's ID, chat room ID, active status, and other relevant information.

        Parameters:
        - chatroom_id (int): The unique identifier of the chat room for which to retrieve agents. Required.

        Returns:
        - list: A list of dictionaries, each representing an agent associated with the chat room.
               Each dictionary contains the keys 'id', 'chatroom_id', 'agent_id', and 'active'.
        """
        info = self.select(
            columns=['id'],
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
                {"column": "active", "value": 1}
            ]
        )
        return info

    def search_chatroom_agent_relation_id(self, chatroom_id: int, agent_id: int):
        """
        Searches for a relation between a chat room and an agent by their IDs.

        This function queries the database to find a relation between the specified chat room ID
        and agent ID. It uses the `select_one` method to check if a record exists that matches both
        the chat room ID and the agent ID. If such a relation exists, the function returns a dictionary
        indicating success; otherwise, it indicates failure.

        :param chatroom_id: The ID of the chat room to search for in the database.
        :type chatroom_id: int

        :param agent_id: The ID of the agent to search for in the database.
        :type agent_id: int

        :return: A dictionary indicating the search result status.
                 - {'status': 1}: If the relation is found in the database.
                 - {'status': 0}: If the relation is not found in the database.
        :rtype: dict
        """
        info = self.select_one(
            columns=[
                'id',
            ],
            conditions=[
                {"column": "chatroom_id", "value": chatroom_id},
                {"column": "agent_id", "value": agent_id},
            ]
        )
        if info is not None:
            return {'status': 1}
        else:
            return {'status': 0}

    def insert_agent(self, data: Dict[str, Any]):
        """
        Insert or update agent relationships for a chatroom.

        Args:
            data (Dict[str, Any]):
                - 'chatroom_id' (int): ID of the chatroom.
                - 'agent' (List[Dict[str, Any]]): List of agents with:
                    - 'agent_id' (int): ID of the agent.
                    - 'active' (bool): Agent's active status.

        Raises:
            ValueError: If any agent is not a dictionary.

        Process:
            - If the agent relation exists, update 'active' status.
            - If not, insert a new relation.
        """
        for agent in data['agent']:

            if not isinstance(agent, dict):
                raise ValueError('Each agent must be a dictionary')

            info = self.select_one(
                columns=[
                    'id',
                ],
                conditions=[
                    {"column": "chatroom_id", "value": data['chatroom_id']},
                    {"column": "agent_id", "value": agent['agent_id']},
                ]
            )

            insert_chatroom_agent_relation = {
                "chatroom_id": data['chatroom_id'],
                "agent_id": agent['agent_id'],
                "active": agent['active'],
            }

            if info is None:
                self.insert(insert_chatroom_agent_relation)
            else:
                self.update(
                    [
                        {"column": "chatroom_id", "value": data['chatroom_id']},
                        {"column": "agent_id", "value": agent['agent_id']},
                    ], {
                        'active': agent['active']
                    }
                )

    def show_chatroom_agent(self, chatroom_id: int = 0): 
        """
        Retrieves a list of agents associated with a specific chat room.

        This function queries the database to find agents that are linked to the given chat room ID.
        The query filters out inactive agents and retrieves additional information about each agent,
        such as their app ID, name, description, icon, and obligations.

        :param chatroom_id: The ID of the chat room for which to retrieve agents.
                            Defaults to 0, which may indicate no chat room is specified.
        :return: A list of dictionaries, each containing information about an agent associated with the chat room.
                 Each dictionary includes the agent's ID, app ID, name, description, icon, icon background, obligations, and active status.
        """
        conditions = [
            {"column": "agents.status", "value": 1},
            {"column": "chatroom_agent_relation.chatroom_id", "value": chatroom_id},
            # {"column": "chatroom_agent_relation.active", "value": 1},
        ]

        list = self.select(
            columns=["agents.id AS agent_id", "agents.app_id", "agents.model_config_id", "agents.user_id", "apps.name", "apps.description", "apps.icon", "apps.avatar", "apps.icon_background", "agents.obligations", "chatroom_agent_relation.active"],
            joins=[
                ["left", "agents", "agents.id = chatroom_agent_relation.agent_id"],
                ["left", "apps", "agents.app_id = apps.id"],
            ],
            conditions=conditions,
            order_by="chatroom_agent_relation.id DESC",
        )

        for item in list:
            if item.get('avatar'):
                item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
            else:
                if item['icon']:
                    item['avatar'] = f"{settings.ICON_URL}/head_icon/{item['icon']}.png"
                else:
                    item['avatar'] = f"{settings.ICON_URL}/head_icon/1.png"

        return list
