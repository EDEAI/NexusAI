from core.database import MySQL
import math
from typing import Any, Dict
from languages import get_language_content
from config import settings
import os
from datetime import datetime


class McpServer(MySQL):
    table_name = "mcp_servers"
    
    def get_server_list(self, page: int = 1, page_size: int = 10, name: str = "") -> dict:
        """
        Retrieves a list of MCP servers with pagination and name filtering.

        Args:
            page: Current page number for pagination
            page_size: Number of items per page
            name: Server name for fuzzy search filtering

        Returns:
            A dictionary containing the server list and pagination information
        """
        conditions = [
            {"column": "status", "value": 1}  # Only query records with normal status
        ]

        if name:
            conditions.append({"column": "name", "op": "like", "value": f"%{name}%"})

        # Get total count
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=conditions
        )["count_id"]

        # Get list data with time fields
        server_list = self.select(
            columns=[
                "server_id",
                "name",
                "description",
                "doc_url",
                "status"
            ],
            conditions=conditions,
            order_by="id DESC",
            limit=page_size,
            offset=(page - 1) * page_size
        )

        return {
            "list": server_list,
            "total_count": total_count,
            "total_pages": math.ceil(total_count / page_size),
            "page": page,
            "page_size": page_size
        } 