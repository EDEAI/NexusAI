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
    