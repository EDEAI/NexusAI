from typing import Any, Dict, List
from core.database import MySQL

class AgentDatasetRelation(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "agent_dataset_relation"
    """
    Indicates whether the `agent_dataset_relation` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False

    
    def get_relations_by_agent_id(self, agent_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all dataset relations for a given agent.

        :param agent_id: int, the ID of the agent.
        :return: A dictionary containing the dataset relations for the agent.
        """
        return self.select(
            columns=[
                'id',
                'dataset_id'
            ],
            conditions=[
                {'column': 'agent_id', 'value': agent_id}
            ]
        )
    