from typing import List, Optional
from pydantic import BaseModel

class McpServerInfo(BaseModel):
    server_id: str
    name: str
    description: Optional[str] = None
    doc_url: Optional[str] = None
    status: int

class McpServerListData(BaseModel):
    list: List[McpServerInfo]
    total_count: int
    total_pages: int
    page: int
    page_size: int

class McpServerListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: McpServerListData 