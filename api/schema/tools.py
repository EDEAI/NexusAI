from typing import Any, Optional
from pydantic import BaseModel

class toolsResponse(BaseModel):
    code: int
    detail: str
    data: Optional[Any] = None  # modified to support nested response structures
