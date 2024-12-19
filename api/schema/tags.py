from pydantic import BaseModel
from typing import Optional

class ResponseBase(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None

class OperationBase(BaseModel):
    msg: Optional[str] = None

class TagResponse(ResponseBase):
    data: Optional[OperationBase] = None

class CreateTagRequest(BaseModel):
    team_id: int
    mode: str
    name: str

class UpdateTagRequest(BaseModel):
    tag_id: int
    name: str

class DeleteTagRequest(BaseModel):
    tag_id: int

class CreateTagBindingRequest(BaseModel):
    tag_id: list[int]
    app_id: int

class DeleteTagBindingRequest(BaseModel):
    tag_id: list[int]
    app_id: int

class TagListBase(BaseModel):
    id: Optional[int] = None
    team_id: Optional[int] = None
    mode: Optional[int] = None
    name: Optional[str] = None

class TagListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[list[TagListBase]] = None

class TageListRequest(BaseModel):
    team_id: int
    mode: int