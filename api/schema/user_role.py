from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class RolesInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RolesListData(BaseModel):
    list: List[RolesInfo]
    total_count: int
    total_pages: int
    page: int
    page_size: int

class RolesListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: RolesListData 

class PermissionInfo(BaseModel):
    id: int
    title: str
    status: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PermissionListData(BaseModel):
    list: List[PermissionInfo]
    total_count: int
    total_pages: int
    page: int
    page_size: int

class PermissionListResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: PermissionListData 

class CreateRoleInfo(BaseModel):
    role_id: Optional[int] = None

class CreateRole(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[CreateRoleInfo] = None

# class PermissionIdModel(BaseModel):
#     permission_id: int

class CreateRoleSchema(BaseModel):
    name: str
    description: str
    list: List[int]

class OperationBase(BaseModel):
    msg: Optional[str] = None

class OperationResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[OperationBase] = None

class RoleDetailRequest(BaseModel):
    role_id: int

class RoleDetailInfo(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    status: int
    team_id: Optional[int] = None
    built_in: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    permissions: List[PermissionInfo]

class RoleDetailResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: RoleDetailInfo