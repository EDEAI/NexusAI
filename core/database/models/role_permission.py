from typing import Dict, Any, List
from core.database import MySQL
import math

class RolePermission(MySQL):
    """
    A class that extends MySQL to manage operations on the role_permission table.
    """
    table_name = "role_permission"
    """
    Indicates whether the `role_permission` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_permission_ids_by_role_id(self, role_id: int) -> list:
        """
        Get all permission_id values for a given role.
        """
        result = self.select(
            columns=["permission_id"],
            conditions=[{"column": "role_id", "value": role_id}]
        )
        return [item["permission_id"] for item in result]