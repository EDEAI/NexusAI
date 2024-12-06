from typing import  Dict, Any, Optional
from pydantic import BaseModel

class toolsResponse(BaseModel):
    code: int
    detail: str
    data: Optional[Dict[str, Any]] = None
