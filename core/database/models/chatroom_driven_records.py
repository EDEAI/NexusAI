from core.database import MySQL


class ChatroomDrivenRecords(MySQL):
    """
    A database model class for managing chatroom driven records.
    Inherits from MySQL base class to handle database operations.
    
    This class provides an interface to interact with the chatroom_driven_records table,
    which stores the relationships between data source runs and data driven runs.
    """
    
    table_name = "chatroom_driven_records"
    """
    The name of the database table this model interacts with.
    """

    have_updated_time = False
    """
    Configuration flag indicating that this table doesn't track update timestamps.
    Set to False to disable automatic update_time management.
    """

    def get_data_by_data_source_run_id(self, data_source_run_id: int):
        """
        Retrieve record information based on the data source run ID.
        
        Args:
            data_source_run_id (int): The unique identifier of the data source run
            
        Returns:
            dict: A dictionary containing the record information with fields:
                - id: The record's unique identifier
                - data_source_run_id: The associated data source run ID
                - data_driven_run_id: The associated data driven run ID
                
        Note:
            Returns None if no matching record is found.
        """
        info = self.select_one(
            columns=[
                'id','data_source_run_id','data_driven_run_id'
            ],
            conditions=[
                {"column": "data_source_run_id", "value": data_source_run_id},
            ]
        )
        return info

    def update_data_driven_run_id(self, id: int, data_source_run_id: int, data_driven_run_id: int):
        """
        Update the data_driven_run_id for a specific record identified by data_source_run_id.
        
        Args:
            data_source_run_id (int): The identifier of the data source run to update
            data_driven_run_id (int): The new data driven run ID to set
            
        Returns:
            bool: True if the update was successful, False otherwise
            
        Note:
            This method updates a single record matching the data_source_run_id.
        """
        info = self.update(
            columns={
                'data_driven_run_id': data_driven_run_id
            },
            conditions=[
                {"column": "data_source_run_id", "value": data_source_run_id},
                {"column": "id", "value": id}
            ]
        )
        return info
