from typing import Any, Dict, List
from core.database import MySQL
import math
from core.database.models.apps import Apps
from core.database.models.agents import Agents
from languages import get_language_content
from collections import deque
from config import settings

from core.database.models.upload_files import UploadFiles
from pathlib import Path
upload_files = UploadFiles()
project_root = Path(__file__).parent.parent.parent


class ChatroomMessages(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "chatroom_messages"
    """
    Indicates whether the `chatroom_messages` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def history_chatroom_messages(self, chatroom_id: int = 0, page: int = 1, page_size: int = 10):
        """
        Retrieves historical chat room messages with pagination.

        This function fetches chat room messages based on the given chat room ID with support for pagination.
        It builds query conditions and performs a database search using the specified page and page size.
        The result includes a list of message records along with total count and pagination details.

        :param chatroom_id: The ID of the chat room whose messages are to be retrieved.
                            Defaults to 0, which may imply no specific chat room is targeted.
        :type chatroom_id: int

        :param page: The page number for pagination. Defaults to 1, indicating the first page.
        :type page: int

        :param page_size: The number of messages to retrieve per page. Defaults to 10.
        :type page_size: int

        :return: A dictionary containing:
                 - "list": A list of message records, potentially adjusted for pagination.
                 - "total_count": Total number of messages found for the chat room.
                 - "total_pages": Total number of pages calculated from `total_count` and `page_size`.
                 - "page": The current page number.
                 - "page_size": The size of the page used to fetch messages.
        :rtype: dict
        """
        # conditions = [
        #     {"column": "chatrooms.id", "value": chatroom_id},
        #     {"column": "chatroom_messages.agent_id", "value": chatroom_id},
        #     {"column": "chatroom_messages.user_id", "value": chatroom_id}
        # ]

        conditions = [
            {"column": "chatrooms.id", "value": chatroom_id, "op": "="},

            [
                {"column": "chatroom_messages.agent_id", "value": 0, "op": "!=", "logic": "or"},
                {"column": "chatroom_messages.user_id", "value": 0, "op": "!="}
            ]
        ]

        total_count = self.select_one(
            aggregates={"id": "count"},
            joins=[
                ["left", "chatrooms", "chatrooms.id = chatroom_messages.chatroom_id"],
                ["left", "agents", "agents.id = chatroom_messages.agent_id"],
                ["left", "apps", "apps.id = agents.app_id"],
            ],
            conditions=conditions,
        )["count_id"]

        all_page = math.ceil(total_count / page_size)

        offset = total_count - (page * page_size)

        if total_count == 0:
            offset = 0

        if offset < 0:
            offset = 1

        if offset > 0:
            offset = offset

        if offset != 0:
            if total_count - (page * page_size) < 0:
                list = self.select(
                    columns=["apps.name", "apps.description", "apps.icon", "apps.avatar", "apps.icon_background",
                             "chatroom_messages.id",
                             "chatroom_messages.chatroom_id", "chatroom_messages.app_run_id",
                             "chatroom_messages.user_id", 'chatroom_messages.file_list',
                             "chatroom_messages.agent_id", "chatroom_messages.ability_id",
                             "chatroom_messages.message", "chatroom_messages.is_read",
                             "chatroom_messages.created_time"],
                    joins=[
                        ["left", "chatrooms", "chatrooms.id = chatroom_messages.chatroom_id"],
                        ["left", "agents", "agents.id = chatroom_messages.agent_id"],
                        ["left", "apps", "apps.id = agents.app_id"],
                    ],
                    conditions=conditions,
                    limit=page_size,
                    offset=0,
                    order_by="chatroom_messages.id ASC",
                )
            else:
                list = self.select(
                    columns=["apps.name", "apps.description", "apps.icon", "apps.avatar", "apps.icon_background", "chatroom_messages.id",
                             "chatroom_messages.chatroom_id", "chatroom_messages.app_run_id", "chatroom_messages.user_id", 'chatroom_messages.file_list',
                             "chatroom_messages.agent_id", "chatroom_messages.ability_id",
                             "chatroom_messages.message", "chatroom_messages.is_read",
                             "chatroom_messages.created_time"],
                    joins=[
                        ["left", "chatrooms", "chatrooms.id = chatroom_messages.chatroom_id"],
                        ["left", "agents", "agents.id = chatroom_messages.agent_id"],
                        ["left", "apps", "apps.id = agents.app_id"],
                    ],
                    conditions=conditions,
                    limit=page_size,
                    offset=offset,
                    order_by="chatroom_messages.id ASC",
                )
            if list:
                for item in list:
                    if item['agent_id'] > 0:
                        item['is_agent'] = 1
                    else:
                        item['is_agent'] = 0
                    item['content'] = item['message']

                    if item.get('avatar'):
                        item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"

                    if item['file_list']:
                        file_list = []
                        for file_value in item['file_list']:
                            if file_value:
                                if isinstance(file_value, int):
                                    # Upload file ID
                                    file_data = upload_files.get_file_by_id(file_value)
                                    file_name = file_data['name'] + file_data['extension']
                                    file_path_relative_to_upload_files = Path(file_data['path']).relative_to('upload_files')
                                    file_url = f"{settings.STORAGE_URL}/upload/{file_path_relative_to_upload_files}"
                                elif isinstance(file_value, str):
                                    if file_value[0] == '/':
                                        file_value = file_value[1:]
                                    file_path = project_root.joinpath('storage').joinpath(file_value)
                                    file_name = file_path.name
                                    file_url = f"{settings.STORAGE_URL}/storage/{file_value}"
                                else:
                                    # This should never happen
                                    raise Exception('Unsupported value type!')
                                file_list.append({
                                    'name': file_name,
                                    'url': file_url
                                })
                        item['file_list'] = file_list

        if offset == 0:
            if total_count > 0:
                list = self.select(
                    columns=["apps.name", "apps.description", "apps.icon", "apps.avatar", "apps.icon_background",
                             "chatroom_messages.id",
                             "chatroom_messages.chatroom_id", "chatroom_messages.app_run_id",
                             "chatroom_messages.user_id", 'chatroom_messages.file_list',
                             "chatroom_messages.agent_id", "chatroom_messages.ability_id",
                             "chatroom_messages.message", "chatroom_messages.is_read",
                             "chatroom_messages.created_time"],
                    joins=[
                        ["left", "chatrooms", "chatrooms.id = chatroom_messages.chatroom_id"],
                        ["left", "agents", "agents.id = chatroom_messages.agent_id"],
                        ["left", "apps", "apps.id = agents.app_id"],
                    ],
                    conditions=conditions,
                    limit=page_size,
                    offset=0,
                    order_by="chatroom_messages.id ASC",
                )
                if list:
                    for item in list:
                        if item['agent_id'] > 0:
                            item['is_agent'] = 1
                        else:
                            item['is_agent'] = 0
                        item['content'] = item['message']

                        if item.get('avatar'):
                            item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
                        
                        if item['file_list']:
                            file_list = []
                            for file_value in item['file_list']:
                                if file_value:
                                    if isinstance(file_value, int):
                                        # Upload file ID
                                        file_data = upload_files.get_file_by_id(file_value)
                                        file_name = file_data['name'] + file_data['extension']
                                        file_path_relative_to_upload_files = Path(file_data['path']).relative_to('upload_files')
                                        file_url = f"{settings.STORAGE_URL}/upload/{file_path_relative_to_upload_files}"
                                    elif isinstance(file_value, str):
                                        if file_value[0] == '/':
                                            file_value = file_value[1:]
                                        file_path = project_root.joinpath('storage').joinpath(file_value)
                                        file_name = file_path.name
                                        file_url = f"{settings.STORAGE_URL}/storage/{file_value}"
                                    else:
                                        # This should never happen
                                        raise Exception('Unsupported value type!')
                                    file_list.append({
                                        'name': file_name,
                                        'url': file_url
                                    })
                            item['file_list'] = file_list
            else:
                list = []

        return {
            "list": list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def search_chatroom_message_asc_id(self, chatroom_id: int = 0):
        """
        Retrieves the most recent message ID for a specified chat room.

        This function queries the database to find the most recently added message ID
        in a specified chat room, identified by its chat room ID. The query orders
        the results in descending order of message ID, effectively returning the highest
        (latest) ID. The function returns the ID of the most recent message.

        :param chatroom_id: The ID of the chat room to search within. Defaults to 0,
                            which may imply no specific chat room is targeted.
        :type chatroom_id: int

        :return: A dictionary containing the most recent message's ID, if found.
                 If no message is found, the return value may be `None`.
        :rtype: dict or None
        """
        conditions = [
            {"column": "chatroom_id", "value": chatroom_id}
        ]

        info = self.select_one(
            columns=["id"],
            conditions=conditions,
            order_by="id DESC",
        )
        return info

    def get_history_list(self, messageList: List[Dict]) -> List[Dict]:
        """
        Get all history messages and the last section of them as JSON strings in an AI prompt.
        """

        messages = []
        for message in messageList:
            agent_id = message['agent_id']
            if agent_id > 0:
                role = 'Agent'
                info = Agents().select_one(
                    columns=[
                        'apps.name'
                    ],
                    joins=[
                        ["left", "apps", "apps.id = agents.app_id"],
                    ],
                    conditions=[
                        {'column': 'id', 'value': agent_id},
                        # {'column': 'status', 'value': 1},
                    ]
                )
                name = info['name']
            else:
                role = 'User'
                name = 'User'
            message_for_llm = {
                'id': agent_id,
                'name': name,
                'role': role,
                'message': message['message']
            }
            if (topic := message['topic']) is not None:
                message_for_llm['topic'] = topic
            messages.append(message_for_llm)
        messages_in_last_section = deque()
        for message in reversed(messages):
            messages_in_last_section.appendleft(message)
            if message['id'] == 0:
                break
        return messages
