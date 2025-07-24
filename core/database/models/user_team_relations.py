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