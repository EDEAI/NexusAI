from pydantic import BaseModel
from typing import Optional, Dict, Any,List
from datetime import datetime

class ReqSkillCreateSchema(BaseModel):
    team_id: int
    user_id: int
    app_id: int
    config: Optional[Dict[str, Any]] = None
    input_variables: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    output_type: int
    output_variables: Optional[Dict[str, Any]] = None
    publish_status: int
    published_time: Optional[datetime] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    status: int

class ReqSkillUpdateSchema(BaseModel):
    config: Optional[Dict[str, Any]] = None
    input_variables: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    output_type: Optional[int] = None
    output_variables: Optional[Dict[str, Any]] = None
    publish_status: Optional[int] = None
    published_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    status: Optional[int] = None
    is_public: Optional[int] = None

class SkillBaseInfoResponseData(BaseModel):
    id: Optional[int] = None
    team_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    input_variables: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    output_type: Optional[int] = None
    output_variables: Optional[Dict[str, Any]] = None
    publish_status: Optional[int] = None
    app_publish_status: Optional[int] = None
    published_time: Optional[datetime] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    status: Optional[int] = None
    is_public: Optional[int] = None
    is_creator: Optional[int] = None
    nickname: Optional[str] = None
class ResSkillBaseInfoSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[SkillBaseInfoResponseData] = None
class SkillListData(BaseModel):
    skill_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
class ResSkillListResponseData(BaseModel):
    list: Optional[List[SkillListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResSkillListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkillListResponseData] = None

class ResSkilCreateData(BaseModel):
    id: Optional[int] = None
    app_id: Optional[int] = None

class ResSkillCreateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkilCreateData] = None

class ResSkillPublishData(BaseModel):
    id: Optional[int] = None
class ResSkillPublishSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkillPublishData] = None
class ReqSkillRunSchema(BaseModel):
    skill_id: Optional[int] = None
    input_dict: Optional[Dict[str, Any]] = None
class  ResSkillRunResponseData(BaseModel):
    outputs: Optional[Dict[str, Any]] = None
class ResSkillRunSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkillRunResponseData] = None

class ReqSkillGenerateSchema(BaseModel):
    user_prompt: Optional[str] = None

class ResSkillGenerateData(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None

class ResSkillGenerateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkillGenerateData] = None

class ReqSkillCorrectionSchema(BaseModel):
    app_run_id: int
    correction_prompt: str

class ResSkillCorrectionData(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None

class ResSkillCorrectionSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResSkillCorrectionData] = None

class ReqSkillDataCreateSchema(BaseModel):
    """Schema for creating or updating skill data"""
    name: Optional[str] = None  # Optional for updates
    description: Optional[str] = None  # Optional for updates
    app_id: Optional[int] = None  # Required for updates
    input_variables: Optional[Dict[str, Any]] = None
    dependencies: Optional[Dict[str, Any]] = None
    code: Optional[str] = None
    output_type: Optional[int] = None
    output_variables: Optional[Dict[str, Any]] = None
    is_public: Optional[int] = None  # Added for app visibility control
    tag_ids: Optional[List[int]] = None  # Added for tag management

class ReqSkillDebugSchema(BaseModel):
    """Schema for skill debugging without saving"""
    name: str
    description: str
    input_variables: dict
    dependencies: dict
    code: Optional[dict] = None
    output_type: int  # 1:text 2:database 3:code 4:document
    output_variables: dict
    test_input: Dict[str, Any]  # Input data for testing