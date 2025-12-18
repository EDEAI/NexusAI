from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApiKeyData(BaseModel):
    """Schema for API key data"""
    id: Optional[int] = None
    app_id: Optional[int] = None
    user_id: Optional[int] = None
    key: Optional[str] = None
    status: Optional[int] = None  # 0: deleted, 1: active
    last_used_time: Optional[datetime] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None


class ApiKeyListData(BaseModel):
    """Schema for API key list data"""
    list: Optional[List[ApiKeyData]] = None
    total_count: Optional[int] = None


class ResApiKeyListSchema(BaseModel):
    """Response schema for API key list"""
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ApiKeyListData] = None


class CreateApiKeyData(BaseModel):
    """Schema for created API key data"""
    id: Optional[int] = None
    key: Optional[str] = None
    app_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[int] = None
    created_time: Optional[datetime] = None


class ResCreateApiKeySchema(BaseModel):
    """Response schema for creating an API key"""
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[CreateApiKeyData] = None


class ResDeleteApiKeySchema(BaseModel):
    """Response schema for deleting an API key"""
    code: Optional[int] = None
    detail: Optional[str] = None