from typing import Any, Dict, List, Optional
from core.database.orm import ORM, Conditions
from datetime import datetime

class MySQL(ORM):

    def __init__(self) -> None:
        """
        Initializes the class by calling the parent class's __init__ method.
        """
        super().__init__()
        
    def insert(self, data: Dict[str, Any]) -> Any:
        """
        Inserts a new record into the {table_name} table.

        :param data: A dictionary containing the data to be inserted.
        :return: The result of the insert operation.
        """
        return super().insert(self.table_name, data)

    def update(self, conditions: Conditions, data: Dict[str, Any]) -> bool:
        """
        Updates records in the {table_name} table based on the specified conditions.

        :param conditions: A dictionary specifying the conditions for the records to be updated.
        :param data: A dictionary containing the data to be updated.
        :return: The result of the update operation.
        """
        if self.have_updated_time:
            data['updated_time'] = datetime.now()
        return super().update(self.table_name, conditions, data)

    def select(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Selects records from the {table_name} table based on the specified keyword arguments.

        :param kwargs: Keyword arguments specifying the conditions and options for the selection.
        :return: A list of dictionaries, each representing a row from the {table_name} table.
        """
        return super().select(self.table_name, **kwargs)
    
    def select_one(self, **kwargs: Any) -> Optional[Dict[str, Any]]:
        """
        Selects records from the {table_name} table based on the specified keyword arguments.

        :param kwargs: Keyword arguments specifying the conditions and options for the selection.
        :return: A list of dictionaries, each representing a row from the {table_name} table.
        """
        return super().select_one(self.table_name, **kwargs)
    
    def soft_delete(self, conditions: Conditions) -> bool:
        """
        Performs a soft delete on records in the {table_name} table based on the specified conditions.

        :param conditions: A dictionary specifying the conditions for the records to be soft deleted.
        :return: The result of the update operation marking the records as deleted.
        """
        return super().update(self.table_name, conditions, {'status': 3})

    def delete(self, conditions: Conditions) -> bool:
        """
        Deletes records from the {table_name} table based on the specified conditions.

        :param conditions: A dictionary specifying the conditions for the records to be deleted.
        :return: The result of the delete operation.
        """
        return super().delete(self.table_name, conditions)