from typing import Any, Dict, List
from core.database import MySQL

class RagRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "rag_records"
    """
    Indicates whether the `rag_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True



