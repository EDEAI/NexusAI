from core.database import MySQL


class AgentChatMessages(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "agent_chat_messages"
    """
    Indicates whether the `agent_chat_messages` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False
    