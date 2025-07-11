from typing import Dict, Any, List
from core.database import MySQL
import math

class Permission(MySQL):
    """
    A class that extends MySQL to manage operations on the permissions table.
    """
    table_name = "permissions"
    """
    Indicates whether the `permissions` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def get_permission_list(self, page: int = 1, page_size: int = 10, name: str = "") -> dict:
        """
        Retrieves a list of permissions with pagination and Chinese title filtering.

        Args:
            page: Current page number for pagination
            page_size: Number of items per page
            name: Permission Chinese title for fuzzy search filtering

        Returns:
            A dictionary containing the permission list and pagination information
        """
        conditions = [
            {"column": "status", "value": 1}  # Only query records with normal status
        ]

        if name:
            conditions.append({"column": "title_cn", "op": "like", "value": f"%{name}%"})

        # Get total count
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions
        )["count_id"]

        # Get list data with time fields
        permission_list = self.select(
            columns=[
                "id",
                "title_cn",
                "title_en",
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
            "list": permission_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        }

    def check_permissions_exist(self, permission_ids: list) -> bool:
        """
        Check if all permission ids in the list exist in the permissions table.
        Args:
            permission_ids: List of permission ids to check
        Returns:
            True if all exist, False otherwise
        """
        if not permission_ids:
            return False
        count = self.select_one(
            aggregates={"id": "count"},
            conditions=[{"column": "id", "op": "in", "value": permission_ids}]
        )["count_id"]
        return count == len(permission_ids) 