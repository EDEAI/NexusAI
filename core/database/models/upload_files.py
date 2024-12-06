from typing import Any, Dict, List
from core.database import MySQL

class UploadFiles(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """
    
    table_name = "upload_files"
    """
    Indicates whether the `upload_files` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False
    
    def get_file_by_id(self, file_id: int) -> Dict[str, Any]:
        """
        Retrieves the file information for the given file ID.

        :param file_id: The ID of the file.
        :return: A dictionary containing the file information.
        """
        file = self.select_one(
            columns=['name', 'path', 'extension'],
            conditions=[
                {'column': 'id', 'value': file_id}
            ]
        )
        return file

    def get_by_team_id(self, file_ids :List[int]) -> List[Dict[str,Any]]:
        """
        Returns a list of file information for the given file IDs.

        :param file_ids: A list of file IDs.
        :return: A list of dictionaries containing file information.
        """
        result = self.select(
            columns=['upload_files.id','users.team_id'],
            joins = [
                ['left','users','upload_files.user_id = users.id']
            ],
            conditions = [
                {'column': 'id', 'op':'in' , 'value': file_ids}
            ],
            group_by = 'upload_files.id'
        )
        return result