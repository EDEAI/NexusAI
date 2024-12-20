from pydantic import BaseModel
from typing import Optional, List

class ResponseBase(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None

class OperationBase(BaseModel):
    msg: Optional[str] = None

class TagResponse(ResponseBase):
    data: Optional[OperationBase] = None

class CreateTagRequest(BaseModel):
    mode: int
    name: str

class UpdateTagRequest(BaseModel):
    tag_id: int
    name: str

class DeleteTagRequest(BaseModel):
    tag_id: int

class CreateTagBindingRequest(BaseModel):
    tag_ids: List[int]
    app_ids: List[int]

class DeleteTagBindingRequest(BaseModel):
    tag_id: List[int]
    app_id: int

class TagListBase(BaseModel):
    id: Optional[int] = None
    mode: Optional[int] = None
    name: Optional[str] = None

class TagListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[List[TagListBase]] = None

class TageListRequest(BaseModel):
    mode: int