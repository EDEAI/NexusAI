from pydantic import BaseModel, Json
from typing import Optional, List, Dict, Any,Union
from datetime import datetime
class RealationInfo(BaseModel):
    apps_id:Optional[int] = None
    name:Optional[str] = None
    mode:Optional[int] = None
    icon:Optional[str] = None
    icon_background:Optional[str] = None

class AppListTagsData(BaseModel):
    id:Optional[int] = None
    name:Optional[str] = None

class AppsListData(BaseModel):
    app_id:Optional[int] = None
    name: Optional[str] = None
    mode:Optional[int] = None
    description: Optional[str] = None
    icon:Optional[str] = None
    icon_background:Optional[str] = None
    execution_times: Optional[int] = None
    publish_status:Optional[int] =None
    published_time:Optional[Union[datetime, None]] = None
    published_creator:Optional[str] = None
    tags:Optional[List[AppListTagsData]] = None
    list:Optional[List[RealationInfo]] = None
    agent_id:Optional[int] = None

class  ResAppsListData(BaseModel):
    list: Optional[List[AppsListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResAppListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResAppsListData] = None

class ReqAppBaseCreateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    mode: Optional[int] = None

class ResAppsCreateData(BaseModel):
   app_id: Optional[int] = None
class ResAppsBaseCreateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[ResAppsCreateData] = None