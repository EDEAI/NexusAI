from typing import Any, Dict, List
from core.database import MySQL
from config import settings

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
                - name (str): The name of the app
                - description (str): The description of the app
                - avatar (str): The avatar URL of the app
        """
        result = self.select(
            columns=[
                'agent_callable_items.id', 
                'agent_callable_items.agent_id', 
                'agent_callable_items.app_id', 
                'agent_callable_items.item_type',
                'apps.name',
                'apps.description',
                'apps.avatar',
                'apps.icon'
            ],
            joins=[
                ["left", "apps", "agent_callable_items.app_id = apps.id"]
            ],
            conditions=[
                {"column": "agent_callable_items.agent_id", "value": agent_id}
            ]
        )

        # Process avatar URLs
        for item in result:
            if item.get('avatar'):
                if item['avatar'].find('head_icon') == -1:
                    item['avatar'] = f"{settings.STORAGE_URL}/upload/{item['avatar']}"
                else:
                    item["avatar"] = f"{settings.ICON_URL}/{item['avatar']}"
            else:
                if item['icon']:
                    item['avatar'] = f"{settings.ICON_URL}/head_icon/{item['icon']}.png"
                else:
                    item['avatar'] = f"{settings.ICON_URL}/head_icon/1.png"

        return result
