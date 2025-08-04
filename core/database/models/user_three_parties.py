from typing import Dict, Any, List
from core.database import MySQL
import math
from datetime import datetime

class UserThreeParties(MySQL):
    """
    A class that extends MySQL to manage operations on the user_three_parties table.
    """
    table_name = "user_three_parties"
    """
    Indicates whether the `user_three_parties` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = False