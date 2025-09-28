from typing import Any, Dict, Optional

from sqlalchemy.util import ordered_column_set

from core.database import MySQL


class NonLLMRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "non_llm_records"
    """
    Indicates whether the `non_llm_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = False
    
    def get_record_by_input_file_id(self, input_file_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a record by input file ID.
        """
        record = self.select_one(
            columns=['output_text'],
            conditions=[
                {'column': 'input_file_id', 'value': input_file_id},
                {'column': 'status', 'value': 3}
            ],
            order_by='id DESC'
        )
        return record
