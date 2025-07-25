from typing import Any, Optional, Dict
from pydantic import BaseModel

class toolsResponse(BaseModel):
    code: int
    detail: str
    data: Optional[Any] = None  # modified to support nested response structures

class PaginatedToolsData(BaseModel):
    """Paginated tools response data"""
    tools: Dict[str, Any]  # The tools data
    total_count: int  # Total number of providers
    total_pages: int  # Total number of pages
    page: int  # Current page number
    page_size: int  # Number of items per page

class PaginatedToolsResponse(BaseModel):
    """Paginated tools response schema"""
    code: int
    detail: str
    data: Optional[PaginatedToolsData] = None
