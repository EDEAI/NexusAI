from core.database import MySQL


class ChatroomDrivenRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "chatroom_driven_records"
    """
    Indicates whether the `chatroom_driven_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False
