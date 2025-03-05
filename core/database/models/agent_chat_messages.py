from core.database import MySQL
import math


class AgentChatMessages(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "agent_chat_messages"
    """
    Indicates whether the `agent_chat_messages` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def history_agent_messages(self, agent_id: int = 0, uid: int = 0, page: int = 1, page_size: int = 10):
        """
        Retrieves historical chat room messages with pagination.

        This function fetches chat room messages based on the given agent ID and user ID with support for pagination.
        It builds query conditions and performs a database search using the specified page and page size.
        The result includes a list of message records along with total count and pagination details.

        :param agent_id: The ID of the agent (from the agent table) whose messages are to be retrieved.
        Defaults to 0, which may imply no specific agent is targeted.
        :type agent_id: int

        :param uid: The ID of the user whose messages are to be retrieved.
        Defaults to 0, which may imply no specific user is targeted.
        :type uid: int

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

        conditions = [
            {"column": "agent_id", "value": agent_id, "op": "="},
            {"column": "user_id", "value": uid, "op": "="},
        ]

        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions,
        )["count_id"]

        offset = total_count - (page * page_size)

        if total_count == 0:
            offset = 0

        if offset < 0:
            offset = 1

        if offset > 0:
            offset = offset
        message_list = []
        if offset != 0:
            if total_count - (page * page_size) < 0:
                message_list = self.select(
                    columns=['id', 'user_id', 'agent_id', 'ability_id', 'agent_run_id', 'message', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'created_time'],
                    conditions=conditions,
                    limit=page_size,
                    offset=0,
                    order_by="id ASC",
                )
            else:
                message_list = self.select(
                    columns=['id', 'user_id', 'agent_id', 'ability_id', 'agent_run_id', 'message', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'created_time'],
                    conditions=conditions,
                    limit=page_size,
                    offset=offset,
                    order_by="id ASC",
                )

        if offset == 0:
            if total_count > 0:
                message_list = self.select(
                    columns=['id', 'user_id', 'agent_id', 'ability_id', 'agent_run_id', 'message', 'prompt_tokens', 'completion_tokens', 'total_tokens', 'created_time'],
                    conditions=conditions,
                    limit=page_size,
                    offset=0,
                    order_by="id ASC",
                )

        return {
            "list": message_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def get_chat_agent_history(self, user_id: int, agent_id: int):
        """
        Retrieves the chat history for a specific user and agent.

        :param user_id: The ID of the user.
        :param agent_id: The ID of the agent.
        :return: A list of chat messages.
        """
        # Query to find the largest id where history_cleared is 1 for the given user and agent
        # Query to find the largest id where history_cleared is 1 for the given user and agent
        conditions = [
            {"column": "history_cleared", "value": 1, "op": "="},
            {"column": "user_id", "value": user_id, "op": "="},
            {"column": "agent_id", "value": agent_id, "op": "="}
        ]

        cleared_messages = self.select_one(
            columns=["id"],
            conditions=conditions,
            order_by='id DESC',  # Order by id descending to get the latest first
        )

        if cleared_messages:
            start_id = cleared_messages['id']
        else:
            start_id = 0

        # Query to select all messages with id greater than the start_id
        conditions = [
            {"column": "id", "value": start_id, "op": ">"},
            {"column": "user_id", "value": user_id},
            {"column": "agent_id", "value": agent_id}
        ]
        messages = self.select(
            columns=["message", "agent_run_id"],
            conditions=conditions,
            order_by='id ASC'
        )
        return messages
