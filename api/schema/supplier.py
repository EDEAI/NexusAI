from pydantic import BaseModel
from typing import Optional, Dict, Any,List

class ResponseBase(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    
class SupplierListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class SupplierRequest(BaseModel):
    supplier_id: Optional[int] = None
    config: Optional[List[Any]] = None

class ModelRequest(BaseModel):
    model_id: Optional[int] = None
    config: Optional[Dict[str, Any]] = None

class ModelSwitchRequest(BaseModel):
    type: Optional[int] = None
    model_id: Optional[int] = None

class OperationBase(BaseModel):
    msg: Optional[str] = None


class OperationResponse(ResponseBase):
    data: Optional[OperationBase] = None

