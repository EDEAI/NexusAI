from typing import Any, Dict, List
from core.database import MySQL

class ToolAuthorizations(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name: str = "tool_authorizations"
    """
    Indicates whether the `tool_authorizations` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def get_tool_info(self,user_id: int, team_id: int,provider:str) -> Dict[str, Any]:
        tool = self.select_one(columns='*',
                                conditions=[
                                    {"column": "user_id", "value": user_id},
                                    {"column": "team_id", "value": team_id},
                                    {"column": "provider", "value": provider},
                                ])
        if not tool:
            return {'status': 2, 'message': 'tool not found'}
        return {'status': 1, 'message': 'ok', 'data': tool}