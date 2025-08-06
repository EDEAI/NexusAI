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
    

    def get_roles_list(self, page: int = 1, page_size: int = 10, status: int = 1, name: str = "", team_id = int) -> dict:
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
            {"column": "status", "value": 1},  # Only query records with normal status
            {"column": "team_id", "op": "in", "value": [team_id, 0]}
        ]

        if name:
            conditions.append({"column": "name", "op": "like", "value": f"%{name}%"})
            conditions.append({"column": "built_in", "op": "!=", "value": 1})

        if status == 1:
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
                    "built_in",
                    "description",
                    "status",
                    "created_at",
                    "updated_at"
                ],
                conditions=conditions,
                order_by="id ASC",
                limit=page_size,
                offset=(page - 1) * page_size
            )
        else:
            total_count = self.select_one(
                aggregates={"id": "count"},
                conditions=conditions
            )["count_id"]

            role_list = self.select(
                columns=[
                    "id",
                    "name",
                    "built_in",
                    "description",
                    "status",
                    "created_at",
                    "updated_at"
                ],
                conditions=conditions,
                order_by="id ASC"
            )

        from languages import get_language_content
        for role in role_list:
            if role.get('built_in') == 1:
                # For built-in roles, the name field contains the language key
                role_key = role['name']  # e.g., 'comprehensive_administrator'
                # Translate role name
                role['name'] = get_language_content(role_key)
                # Set role description using the corresponding _desc key
                role['description'] = get_language_content(f"{role_key}_desc")
        if status == 1:
            total_pages =  math.ceil(total_count / page_size)
            page_size = page_size
        else:
            total_pages = 1
            page_size = total_count
        return {
            "list": role_list,
            "total_count": total_count,
            "total_pages": total_pages,
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

    def check_role_deletable(self, role_id: int, mode: int = None) -> bool:
        """
        Check if a role can be deleted based on its name and mode.

        Args:
            role_id (int): The ID of the role to check.
            mode (int): The mode value (1-5) corresponding to different administrator types.
                       1: agent_administrator
                       2: workflow_administrator  
                       3: knowledge_base_administrator
                       4: skill_administrator
                       5: roundtable_administrator

        Returns:
            bool: True if the role can be deleted, False otherwise.
        """
        # Define the mode to role name mapping
        mode_role_mapping = {
            1: 'agent_administrator',
            2: 'workflow_administrator', 
            3: 'knowledge_base_administrator',
            4: 'skill_administrator',
            5: 'roundtable_administrator'
        }
        
        # Query the role by ID with built_in = 0 condition
        role = self.select_one(
            columns=['name'],
            conditions=[
                {"column": "id", "value": role_id},
                {"column": "built_in", "value": 1},
                {"column": "status", "value": 1}
            ]
        )
        
        # If role not found or query returns None, return True (can be deleted)
        if not role:
            return True
        
        role_name = role.get('name', '')
        
        # If role name is comprehensive_administrator, always return True
        if role_name == 'comprehensive_administrator':
            return True
        
        # If mode is provided, check if role name matches the mode
        if mode is not None and mode in mode_role_mapping:
            expected_role_name = mode_role_mapping[mode]
            # Return True if role name matches the expected role for this mode
            return role_name == expected_role_name
        
        # If no mode provided or invalid mode, check if role is in restricted list
        restricted_roles = [
            'agent_administrator', 
            'workflow_administrator',
            'skill_administrator',
            'roundtable_administrator',
            'knowledge_base_administrator'
        ]
        
        # If role name is not in restricted list, return True (can be deleted)
        if role_name not in restricted_roles:
            return True
        
        # For other restricted roles without matching mode, return False
        return False

    