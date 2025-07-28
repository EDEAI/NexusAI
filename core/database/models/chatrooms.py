from core.database import MySQL
from core.database.models.agents import Agents
from core.database.models.chatroom_agent_relation import ChatroomAgentRelation
import math
from typing import Any, Dict
import os
from config import settings
from datetime import datetime, timedelta


class Chatrooms(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "chatrooms"
    """
    Indicates whether the `chatrooms` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def search_agent_id(self, agent_id: int):
        """
        Searches for an agent by its ID.

        This function queries the database to find an agent with the specified ID in the Agents table.
        It uses the `select_one` method from the `Agents` model to perform the search based on
        the provided agent ID. If an agent with the given ID exists, the function returns a dictionary
        indicating success. Otherwise, it indicates failure.

        :param agent_id: The ID of the agent to search for in the database.
        :type agent_id: int

        :return: A dictionary indicating the search result status.
                 - {'status': 1}: If the agent is found in the database.
                 - {'status': 0}: If the agent is not found in the database.
        :rtype: dict
        """
        agent_model = Agents()
        info = agent_model.select_one(
            columns=[
                'id',
            ],
            conditions=[
                {"column": "id", "value": agent_id},
            ]
        )
        if info is not None:
            return {'status': 1}
        else:
            return {'status': 0}
        
    def get_chatroom_by_id(self, chatroom_id: int) -> Dict[str, Any]:
        """
        Retrieves a chatroom record by its ID.

        This function queries the database to find a chatroom with the specified ID.
        It joins with the apps table to get the chatroom name and checks that the
        chatroom status is active.

        :param chatroom_id: The ID of the chatroom to retrieve.
        :type chatroom_id: int

        :return: A dictionary containing the chatroom information.
        :rtype: Dict[str, Any]

        :raises AssertionError: If no chatroom is found with the given ID.
        """
        chatroom = self.select_one(
            columns=[
                'apps.name'
            ],
            joins=[['inner', 'apps', 'chatrooms.app_id = apps.id']],
            conditions=[
                {'column': 'id', 'value': chatroom_id},
                {'column': 'status', 'value': 1}
            ]
        )
        assert chatroom
        return chatroom

    def search_chatrooms_id(self, chatroom_id: int, user_id: int):
        """
        Retrieves information about a chat room by its ID.

        This function queries the database for a chat room with the specified ID.
        If the chat room exists, it returns a dictionary containing the chat room's
        maximum round, app ID, and a status code indicating success.

        :param chatroom_id: The ID of the chat room to search for.
        :return: A dictionary containing the chat room's information and a status code.
                 - If the chat room is found, the status code is 1.
                 - If the chat room is not found, the status code is 0.
        """
        info = self.select_one(
            columns=[
                'id', 'max_round', 'app_id', 'status', 'chat_status', 'smart_selection', 'initial_message_id'
            ],
            conditions=[
                {"column": "id", "value": chatroom_id},
                {"column": "user_id", "value": user_id},
                {"column": "status", "value": 1},
            ]
        )
        if info is not None:
            return {'status': 1, 'chat_status':info['chat_status'] ,'max_round': info['max_round'], 'app_id': info['app_id'], 'chatroom_status': info['status'], 'smart_selection': info['smart_selection'], 'initial_message_id': info['initial_message_id']}
        else:
            return {'status': 0}

    def all_chat_room_list(self, page: int = 1, page_size: int = 10, uid: int = 0, name: str = "", is_temporary: bool = False):
        """
        Retrieves a list of chat rooms with pagination, filtering by user ID and chat room name.

        :param page: The page number for pagination.
        :param page_size: The number of items per page.
        :param uid: The ID of the user to filter chat rooms by.
        :param name: The name of the chat room to filter by.
        :return: A dictionary containing the list of chat rooms, total count, total pages, current page, and page size.
        """
        conditions = [
            {"column": "chatrooms.status", "value": 1},
            {"column": "apps.status", "value": 1},
            {"column": "apps.mode", "value": 5},
            {"column": "chatrooms.user_id", "value": uid},
            {"column": "chatrooms.chat_agent_id", "value": 0},
        ]

        if is_temporary:    
            # conditions.append({"column": "chatrooms.is_temporary", "value": 1})
            conditions.append({"column": "chatrooms.is_temporary", "op": "in", "value": [1, 0]})
        else:
            conditions.append({"column": "chatrooms.is_temporary", "value": 0})

        if name:
            conditions.append({"column": "apps.name", "op": "like", "value": "%" + name + "%"})

        total_count = self.select_one(
            aggregates={"id": "count"},
            joins=[
                ["left", "apps", "chatrooms.app_id = apps.id"],
            ],
            conditions=conditions,
        )["count_id"]

        chatroom_list = self.select(
            columns=[
                "apps.name",
                "apps.description",
                "chatrooms.id as chatroom_id",
                "chatrooms.chat_status",
                "chatrooms.active",
                "chatrooms.status as chatroom_status",
                "chatrooms.smart_selection",
                "chatrooms.is_temporary",
                "chatrooms.last_chat_time",
                "apps.id as app_id"
            ],
            joins=[
                ["left", "apps", "chatrooms.app_id = apps.id"]
            ],
            conditions=conditions,
            order_by="chatrooms.last_chat_time DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        for chat_item in chatroom_list:
            chat_item['last_chat_time_display'] = self.format_wechat_time(chat_item['last_chat_time'])
            chat_item['agent_list'] = []
            agent_list = ChatroomAgentRelation().select(
                columns=["agent_id", "chatroom_id"],
                conditions=[
                    {"column": "chatroom_id", "value": chat_item['chatroom_id']}
                ],
                order_by="id DESC"
            )

            if agent_list:
                for agent_item in agent_list:
                    if agent_item['agent_id'] > 0:
                        agent_data = Agents().select_one(
                            columns=["apps.name", "apps.description", "agents.id AS agent_id", 
                                   "agents.app_id", "apps.icon", "apps.avatar",
                                   "apps.icon_background", "agents.obligations"],
                            conditions=[
                                {"column": "id", "value": agent_item['agent_id']}
                            ],
                            joins=[
                                ["left", "apps", "apps.id = agents.app_id"],
                            ]
                        )
                        
                        if agent_data and agent_data.get('avatar'):
                            if agent_data['avatar'].find('head_icon') == -1:
                                agent_data['avatar'] = f"{settings.STORAGE_URL}/upload/{agent_data['avatar']}"
                        else:
                            if agent_data['icon']:
                                agent_data['avatar'] = f"{settings.ICON_URL}/head_icon/{agent_data['icon']}.png"
                            else:
                                agent_data['avatar'] = f"{settings.ICON_URL}/head_icon/1.png"
                            
                        chat_item['agent_list'].append(agent_data)

        for room in chatroom_list:
            if 'agent_list' in room and isinstance(room['agent_list'], list):
                room['agent_list'] = [a for a in room['agent_list'] if isinstance(a, dict)]

        return {
            "list": chatroom_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }
    
    @staticmethod
    def format_wechat_time(dt: datetime) -> str:
        now = datetime.now()
        today = now.date()
        if dt is None:
            return ""
        if isinstance(dt, str):
            try:
                dt = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S")
            except Exception:
                return dt  # 保底返回原始字符串

        delta = today - dt.date()
        if delta.days == 0:
            # 今天
            hour = dt.hour
            if hour < 12:
                return f"上午 {dt.strftime('%H:%M')}"
            else:
                return f"下午 {dt.strftime('%H:%M')}"
        elif delta.days == 1:
            return "昨天"
        elif delta.days == 2:
            return "前天"
        elif dt.year == now.year:
            return dt.strftime("%m/%d")
        else:
            return dt.strftime("%Y/%m/%d")
        
    def recent_chatroom_list(self, chatroom_id: int, uid: int = 0):
        """
        Retrieves a list of the most recently active chat rooms for a given user, excluding a specific chat room.

        This function queries the database to find the most recently active chat rooms for the specified user,
        based on the 'last_run_time' from the 'app_runs' table. It excludes the chat room with the provided chatroom_id.
        It then retrieves the associated agents for each chat room in the list.

        Parameters:
        - chatroom_id (int): The ID of the chat room to exclude from the list. Required.
        - uid (int): The ID of the user to retrieve chat rooms for. Defaults to 0.

        Returns:
        - dict: A dictionary containing the list of recent chat rooms, with each chat room including its associated agents.
        """
        try:
            query = f"""
                SELECT apps.name, apps.description, chatrooms.id as chatroom_id, chatrooms.active, apps.id as app_id
                FROM chatrooms
                INNER JOIN apps ON chatrooms.app_id = apps.id
                INNER JOIN (
                    SELECT chatroom_id, MAX(created_time) as last_run_time
                    FROM app_runs
                    GROUP BY chatroom_id
                ) AS last_runs ON chatrooms.id = last_runs.chatroom_id
                WHERE chatrooms.status = 1 AND chatrooms.is_temporary = 0 AND chatrooms.chat_agent_id = 0 AND apps.status = 1 AND apps.mode = 5 AND chatrooms.user_id = {uid} AND chatrooms.id != {chatroom_id}
                ORDER BY last_run_time DESC
                LIMIT 5
            """
            list = self.execute_query(query)
            rows = list.mappings().all()
            chatrooms = [dict(row) for row in rows]
            for chatroom in chatrooms:
                chatroom_id = chatroom.get("chatroom_id")
                if chatroom_id:
                    agent_list = ChatroomAgentRelation().show_chatroom_agent(chatroom_id)
                    chatroom["agent_list"] = agent_list
            return {"list": chatrooms}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"list": []}

    def get_chatrooms_by_agent(self, agent_id: int, page: int = 1, page_size: int = 10, 
                                show_all: bool = False, current_user_id: int = 0):
        """
        Retrieve chat rooms that exclusively contain the specified agent.
        Only chat rooms where the agent list has exactly one entry and that agent's id equals agent_id are returned.
        Supports pagination unless show_all is True.
        """
        conditions = [
            {"column": "chatrooms.status", "value": 1},
            {"column": "apps.status", "value": 1},
            {"column": "apps.mode", "value": 5},
            {"column": "chatroom_agent_relation.agent_id", "value": agent_id},
            {"column": "chatrooms.user_id", "value": current_user_id},
            {"column": "chatrooms.is_temporary", "value": 1},
        ]
        joins = [
            ["inner", "chatroom_agent_relation", "chatrooms.id = chatroom_agent_relation.chatroom_id"],
            ["left", "apps", "chatrooms.app_id = apps.id"]
        ]
        # Fetch the list based on pagination or all records
        if show_all:
            chat_list = self.select(
                columns=[
                    "apps.name", "apps.description", "chatrooms.id as chatroom_id", "chatrooms.chat_status",
                    "chatrooms.active", "chatrooms.status as chatroom_status", "chatrooms.smart_selection",
                    "apps.id as app_id", "chatrooms.created_time", "chatrooms.last_chat_time"
                ],
                joins=joins,
                conditions=conditions,
                order_by="chatrooms.id DESC,chatrooms.last_chat_time DESC"
            )
        else:
            chat_list = self.select(
                columns=[
                    "apps.name", "apps.description", "chatrooms.id as chatroom_id", "chatrooms.chat_status",
                    "chatrooms.active", "chatrooms.status as chatroom_status", "chatrooms.smart_selection",
                    "apps.id as app_id", "chatrooms.created_time", "chatrooms.last_chat_time"
                ],
                joins=joins,
                conditions=conditions,
                order_by="chatrooms.id DESC , chatrooms.last_chat_time DESC",
                limit=page_size,
                offset=(page - 1) * page_size
            )

        # Populate agent list for each chat room
        for chat_item in chat_list:
            chat_item['agent_list'] = []
            agent_relations = ChatroomAgentRelation().select(
                columns=["agent_id"],
                conditions=[{"column": "chatroom_id", "value": chat_item['chatroom_id']}],
                order_by="id DESC"
            )
            for rel in agent_relations:
                if rel['agent_id'] > 0:
                    agent_info = Agents().select_one(
                        columns=["apps.name", "apps.description", "agents.id AS agent_id", "agents.app_id",
                                 "apps.icon", "apps.avatar", "apps.icon_background", "agents.obligations"],
                        conditions=[{"column": "id", "value": rel['agent_id']}],
                        joins=[["left", "apps", "apps.id = agents.app_id"]]
                    )
                    if agent_info:
                        if agent_info.get('avatar'):
                            if item['avatar'].find('head_icon') == -1:
                                agent_info['avatar'] = f"{settings.STORAGE_URL}/upload/{agent_info['avatar']}"
                        else:
                            if agent_info['icon']:
                                agent_info['avatar'] = f"{settings.ICON_URL}/head_icon/{agent_info['icon']}.png"
                            else:
                                agent_info['avatar'] = f"{settings.ICON_URL}/head_icon/1.png"
                        chat_item['agent_list'].append(agent_info)

        # Filter: only keep chatrooms where the agent list has exactly one agent and that agent's id equals agent_id.
        filtered_list = [
            room for room in chat_list
            if len(room.get('agent_list', [])) == 1 and room['agent_list'][0]['agent_id'] == agent_id
        ]
        total = len(filtered_list)
        total_pages = 1 if show_all else ((total + page_size - 1) // page_size)
        for room in filtered_list:
            if 'agent_list' in room and isinstance(room['agent_list'], list):
                room['agent_list'] = [a for a in room['agent_list'] if isinstance(a, dict)]
        return {
            "list": filtered_list,
            "total_count": total,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size
        }
