from typing import Any, Dict, List
from core.database import MySQL

from core.database.models.upload_files import UploadFiles
from pathlib import Path
upload_files = UploadFiles()
project_root = Path(__file__).parent.parent.parent


class MCPToolUseRecords(MySQL):
    """
    A class that extends MySQL to manage operations on the {table_name} table.
    """

    table_name = "mcp_tool_use_records"
    """
    Indicates whether the `mcp_tool_use_records` table has an `update_time` column that tracks when a record was last updated.
    """
    have_updated_time = True
    