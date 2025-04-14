from typing import Any, Dict, List
from core.database import MySQL

class AgentCallableItems(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "agent_callable_items"
    """
    Indicates whether the `agent_callable_items` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    def get_callable_items_by_agent_id(self, agent_id: int):
        """
        Get a list of callable items for a specific agent.

        This method queries the agent_callable_items table to retrieve all callable items (skills or workflows)
        associated with the specified agent.

        Args:
            agent_id (int): The unique identifier of the agent to query callable items for.

        Returns:
            list: A list of dictionaries containing callable item information. Each dictionary includes:
                - id (int): The unique identifier of the callable item
                - agent_id (int): The ID of the agent
                - app_id (int): The ID of the skill or workflow
                - item_type (int): The type of item (1: Skill, 2: Workflow)
        """
        return self.select(
            columns=[
                'id', 'agent_id', 'app_id', 'item_type'
            ],
            conditions=[
                {"column": "agent_id", "value": agent_id}
            ]
        )
