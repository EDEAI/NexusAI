from typing import Dict, Any, List
from core.database import MySQL

class MCPServers(MySQL):
    """
    A class that extends MySQL to manage operations on the mcp_servers table.
    """
    table_name = "mcp_servers"
    """
    Indicates whether the `mcp_servers` table has an `updated_time` column that tracks when a record was last updated.
    """
    have_updated_time = True

    def exists(self, server_id: str) -> bool:
        """
        Check if a server already exists
        
        :param server_id: Unique identifier of the server
        :return: True if exists, False otherwise
        """
        result = self.select(
            columns=['id'],
            conditions={'column': 'server_id', 'value': server_id},
            limit=1
        )
        return len(result) > 0
    
    def insert_server(self, server: Dict[str, Any]) -> int:
        """
        Insert a new MCP server record
        
        :param server: Dictionary containing server information, must include server_id, name, description and doc_url
        :return: ID of the newly inserted record, or 0 if insertion fails
        """
        # Validate required fields
        required_fields = ['server_id', 'name', 'description', 'doc_url']
        for field in required_fields:
            if field not in server or not server[field]:
                raise ValueError(f"Missing required field: {field}")
        
        # Check if server already exists
        if self.exists(server['server_id']):
            # Update existing record
            self.update(
                data={
                    'name': server['name'],
                    'description': server['description'],
                    'doc_url': server['doc_url'],
                    'updated_time': 'CURRENT_TIMESTAMP'
                },
                conditions={'column': 'server_id', 'value': server['server_id']}
            )
            
            # Return ID of existing record
            result = self.select_one(
                columns=['id'],
                conditions={'column': 'server_id', 'value': server['server_id']}
            )
            return result['id'] if result else 0
        else:
            # Insert new record
            insert_data = {
                'server_id': server['server_id'],
                'name': server['name'],
                'description': server['description'],
                'doc_url': server['doc_url']
            }
            return self.insert(insert_data)
    
    def get_all_servers(self, page: int = 1, page_size: int = 20, status: int = 1) -> Dict[str, Any]:
        """
        Get all MCP servers list with pagination
        
        :param page: Page number, default is 1
        :param page_size: Number of items per page, default is 20, set to 0 to get all servers
        :param status: Status filter, default is 1 (normal)
        :return: Dictionary containing server list and pagination information
        """
        # Query total count
        total_count = self.select_one(
            aggregates={"id": "count"},
            conditions=[{"column": 'status', "value": status}]
        )['count_id']
        
        # Query list data
        query_params = {
            'columns': [
                'id', 'server_id', 'name', 'description', 'doc_url', 'created_time', 'updated_time'
            ],
            'conditions': [{"column": 'status', "value": status}],
            'order_by': 'id DESC'
        }
        
        if page_size > 0:
            query_params['limit'] = page_size
            query_params['offset'] = (page - 1) * page_size
        
        servers = self.select(**query_params)
        
        # Calculate total pages
        import math
        total_pages = math.ceil(total_count / page_size) if page_size > 0 else 1
        
        return {
            "list": servers,
            "total_count": total_count,
            "total_pages": total_pages,
            "page": page,
            "page_size": page_size
        }
    
    def get_server_by_id(self, server_id: str) -> Dict[str, Any]:
        """
        Get server information by server_id
        
        :param server_id: Unique identifier of the server
        :return: Dictionary containing server information
        """
        server = self.select_one(
            columns=['id', 'server_id', 'name', 'description', 'doc_url', 'created_time', 'updated_time'],
            conditions=[
                {'column': 'server_id', 'value': server_id},
                {'column': 'status', 'value': 1}
            ]
        )
        
        if not server:
            raise ValueError(f"Server does not exist or is disabled: {server_id}")
        
        return server 