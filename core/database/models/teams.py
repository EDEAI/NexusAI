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

    def get_personal_workspace_team_id(self) -> int:
        """
        Query and get the team ID for the personal workspace (type=2).

        :return: The team ID if found, otherwise None.
        """
        team = self.select_one(
            columns=["id"],
            conditions=[
                {"column": "type", "value": 2},
                {"column": "status", "value": 1}
            ]
        )
        if team:
            return team["id"]
        return None

    def get_team_type_by_id(self, team_id: int) -> int:
        """
        根据team_id查询对应的type字段。
        :param team_id: 团队ID
        :return: type字段的值，如果未找到则返回None。
        """
        team = self.select_one(
            columns=["type"],
            conditions=[
                {"column": "id", "value": team_id},
                {"column": "status", "value": 1}
            ]
        )
        if team:
            return team["type"]
        return None