from typing import Any, Dict, List
from core.database import MySQL

class Teams(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "teams"
    """
    Indicates whether the `teams` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True