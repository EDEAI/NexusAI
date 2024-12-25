from pydantic import BaseModel
from typing import Optional, List

class ResponseBase(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None

class TagdataBase(BaseModel):
    id: Optional[int] = None
    team_id: Optional[int] = None
    name: Optional[str] = None

class TagResponse(ResponseBase):
    data: Optional[TagdataBase] = None

class CreateTagRequest(BaseModel):
    mode: int
    name: str

class UpdateTagRequest(BaseModel):
    name: str

class DeleteTagRequest(BaseModel):
    tag_id: int

class CreateTagBindingRequest(BaseModel):
    tag_ids: List[int]
    app_ids: List[int]

class TagListBase(BaseModel):
    id: Optional[int] = None
    mode: Optional[int] = None
    name: Optional[str] = None
    reference_count: Optional[int] = None

class TagsListResponse(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[List[TagListBase]] = None