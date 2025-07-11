from typing import Dict, Any, List
from core.database import MySQL
import math

class Roles(MySQL):
    """
    A class that extends MySQL to manage operations on the roles table.
    """
    table_name = "roles"
    """
    Indicates whether the `roles` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = False
    

    def get_roles_list(self, page: int = 1, page_size: int = 10, name: str = "") -> dict:
        """
        Retrieves a list of roles with pagination and name filtering.

        Args:
            page: Current page number for pagination
            page_size: Number of items per page
            name: Role name for fuzzy search filtering

        Returns:
            A dictionary containing the role list and pagination information
        """
        conditions = [
            {"column": "status", "value": 1}  # Only query records with normal status
        ]

        if name:
            conditions.append({"column": "name", "op": "like", "value": f"%{name}%"})

        # Get total count
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions
        )["count_id"]

        # Get list data with time fields
        role_list = self.select(
            columns=[
                "id",
                "name",
                "description",
                "status",
                "created_at",
                "updated_at"
            ],
            conditions=conditions,
            order_by="id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        return {
            "list": role_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def get_role_by_id(self, role_id: int) -> Dict[str, Any]:
        """
        Get a single role by its ID.

        Args:
            role_id (int): The ID of the role to retrieve.

        Returns:
            Dict[str, Any]: A dictionary containing the role information.
        """
        role = self.select_one(
            columns=[
                'id',
                'name',
                'description',
                'status',
                'created_at',
                'updated_at'
            ],
            conditions=[
                {"column": "id", "value": role_id},
                {"column": "status", "value": 1}
            ]
        )
        return role