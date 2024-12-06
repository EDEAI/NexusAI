from typing import Any, Dict, List
from core.database import MySQL

class AgentAbilities(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "agent_abilities"
    """
    Indicates whether the `agent_abilities` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
        
    def get_ability_by_id(self, ability_id: int) -> Dict[str, Any]:
        ability = self.select_one(
            columns=[
                'name',
                'content',
                'output_format'
            ],
            conditions=[
                {'column': 'id', 'value': ability_id},
                {'column': 'status', 'value': 1}
            ]
        )
        assert ability, "No available ability!"
        return ability
    
    def get_abilities_by_agent_id(self, agent_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves the abilities associated with the specified agent ID.

        :param agent_id: int, the ID of the agent.
        :return: A list of dictionaries, each representing an ability associated with the agent.
        """
        return self.select(
            columns=[
                'id',
                'name',
                'content',
                'output_format'
            ],
            conditions=[
                {'column': 'agent_id', 'value': agent_id},
                {'column': 'status', 'value': 1}
            ]
        )  
    