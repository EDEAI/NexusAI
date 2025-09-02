from typing import Dict, Any, List
from core.database import MySQL
import math
from datetime import datetime

class UserTeamRelations(MySQL):
    """
    A class that extends MySQL to manage operations on the user_team_relations table.
    """
    table_name = "user_team_relations"
    """
    Indicates whether the `user_team_relations` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    def ensure_team_id_exists(self, team_id: int, email: str, role: int, role_id: int) -> None:
        """
        Ensure the given team_id exists in the user_team_relations table. If not, insert it.
        :param team_id: The team ID to check/insert.
        :param email: The email to str (optional, default None).
        """
        from core.database.models.users import Users
        current_time = datetime.now()
        user_id = Users().select_one(columns=['id','inviter_id'], conditions=[{'column': 'email', 'value': email}, {'column': 'status', 'value': 1}])
        if user_id:
            conditions = [
                {"column": "team_id", "value": team_id},
                {"column": "user_id", "value": user_id['id']}
            ]
            exists = self.select_one(columns=["id"], conditions=conditions)
            if not exists:
                data = {
                    "team_id": team_id,
                    "user_id": user_id['id'],
                    "inviter_id": user_id['inviter_id'],
                    "role": role,
                    "role_id": role_id,
                    "created_time": current_time
                }
                self.insert(data)

    def update_user_position(self, user_id: int, team_id: int, position: str) -> bool:
        """
        Update the position of a user in a specific team.
        :param user_id: The user ID.
        :param team_id: The team ID.
        :param position: The new position to set.
        :return: True if update was successful, False otherwise.
        """
        conditions = [
            {"column": "user_id", "value": user_id},
            {"column": "team_id", "value": team_id}
        ]
        
        data = {"position": position}
        
        result = self.update(data=data, conditions=conditions)
        return result

    def get_user_team_relation(self, user_id: int, team_id: int) -> Dict[str, Any]:
        """
        Get the user team relation record by user_id and team_id.
        :param user_id: The user ID.
        :param team_id: The team ID.
        :return: Dictionary containing all columns of the matching record, or None if not found.
        """
        conditions = [
            {"column": "user_id", "value": user_id},
            {"column": "team_id", "value": team_id}
        ]
        
        return self.select_one(columns='*',conditions=conditions)

    def get_secure_admin_user_ids(self, team_id: int) -> List[int]:
        """
        Get the list of admin user_ids in a team EXCLUDING users whose password equals the default 'nexus_ai123456'.

        :param team_id: The team ID.
        :return: A list of user IDs that are admins with non-default passwords.
        """
        rows = self.select(
            columns=['user_team_relations.user_id', 'users.password'],
            conditions=[
                {'column': 'user_team_relations.team_id', 'value': team_id},
                {'column': 'user_team_relations.role', 'value': 1}
            ],
            joins=[
                ["left", "users", "user_team_relations.user_id = users.id"]
            ]
        )
        if not rows:
            return []
    def get_user_role_by_user_and_team(self, user_id: int, team_id: int) -> int:
        """
        Get the user role by user_id and team_id.
        :param user_id: The user ID.
        :param team_id: The team ID.
        :return: The role value (integer), or None if not found.
        """
        conditions = [
            {"column": "user_id", "value": user_id},
            {"column": "team_id", "value": team_id}
        ]
        
        result = self.select_one(columns=["role"], conditions=conditions)
        return result['role'] if result else None