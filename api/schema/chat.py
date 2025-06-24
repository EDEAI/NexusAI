from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Literal
from datetime import datetime

class ResponseBase(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None


class ChatRoomInfoBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chatroom_id: Optional[int] = None
    app_id: Optional[int] = None
    chat_status: Optional[int] = None
    active: Optional[int] = None
    chatroom_status: Optional[int] = None
    smart_selection: Optional[int] = None



class AgentModel(BaseModel):
    agent_id: int
    active: int


class ReqAgentSettingSchema(BaseModel):
    active: int


class ReqChatroomCreateSchema(BaseModel):
    name: str
    description: str
    max_round: int
    agent: List[AgentModel]
    is_temporary: int = 0


class ReqChatroomUpdateSchema(BaseModel):
    name: str
    description: str
    max_round: int
    agent: List[AgentModel]


class AgentListData(BaseModel):
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    obligations: Optional[str] = None


class AgentListResponseData(BaseModel):
    list: Optional[List[AgentListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ResAgentListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentListResponseData] = None


class AgentInfo(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    avatar: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    obligations: Optional[str] = None


class ChatRoomInfo(ChatRoomInfoBase):
    agent_list: Optional[List[AgentInfo]] = None


class ChatRoomPageList(BaseModel):
    list: Optional[List[ChatRoomInfo]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ChatRoomListResponse(ResponseBase):
    data: Optional[ChatRoomPageList] = None


class CreateChatRoomInfo(BaseModel):
    chatroom_id: Optional[int] = None

class CreateChatRoomResponse(ResponseBase):
    data: Optional[CreateChatRoomInfo] = None

class UpdateChatRoomResponse(ResponseBase):
    data: Optional[CreateChatRoomInfo] = None


class ChatRoomDetailAgentBase(BaseModel):
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    type: Optional[str] = None
    user_id: Optional[int] = None
    obligations: Optional[str] = None
    active: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    avatar: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    support_image: Optional[int] = None


class RecentChatRoomInfoBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    chatroom_id: Optional[int] = None
    active: Optional[int] = None
    app_id: Optional[int] = None
    agent_list: Optional[List[ChatRoomDetailAgentBase]] = None


class RecentChatRoomList(BaseModel):
    list: Optional[List[RecentChatRoomInfoBase]] = None


class RecentChatRoomListResponse(ResponseBase):
    data: Optional[RecentChatRoomList] = None


class OperationBase(BaseModel):
    msg: Optional[str] = None

class OperationResponse(ResponseBase):
    data: Optional[OperationBase] = None


class ChatRoomDetailBase(BaseModel):
    id: Optional[int] = None
    team_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[int] = None
    execution_times: Optional[int] = None


class ChatRoomDetailInfo(BaseModel):
    chat_info: Optional[ChatRoomDetailBase] = None
    agent_list: Optional[List[ChatRoomDetailAgentBase]] = None
    max_round: Optional[int] = None
    chatroom_status: Optional[int] = None
    smart_selection: Optional[int] = None
    chat_status: Optional[int] = None

class ChatRoomDetailResponse(ResponseBase):
    data: Optional[ChatRoomDetailInfo] = None

class ChatRoomResponseBase(ResponseBase):
    data: Dict[str, Any]


class ToggleSmartSelectionSwitch(BaseModel):
    smart_selection: Literal[0, 1]


class ChatHistorySummary(BaseModel):
    app_id: Optional[int] = None
    app_run_id: Optional[int] = None
    status: Optional[int] = None
    corrected_parameter: str = None


class ChatSingleMessage(BaseModel):
    message: str = None


class ChatHistoryMessageSummary(BaseModel):
    app_run_id: str = None
    corrected_parameter: str = None


class ChatRoomHistoryList(BaseModel):
    list: Optional[List[ChatRoomInfo]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

# chat_room_history
class ChatRoomHistory(ResponseBase):
    data: None

class SourceRun(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None 
    status: Optional[int] = None
    created_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    total_tokens: Optional[int] = None
    summary: Optional[str] = None

class SummaryCorrection(BaseModel):
    created_time: Optional[datetime] = None
    user_prompt: Optional[str] = None
    correct_prompt: Optional[Dict[str, Any]] = None
    corrected_summary: Optional[str] = None

class TargetApp(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    mode: Optional[int] = None

class TargetRun(BaseModel):
    id: Optional[int] = None
    app: Optional[TargetApp] = None
    agent_id: Optional[int] = None
    workflow_id: Optional[int] = None
    name: Optional[str] = None
    apps_name: Optional[str] = None
    status: Optional[int] = None
    created_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    inputs: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    total_tokens: Optional[int] = None
    percentage: Optional[int] = None

class ChatHistoryItem(BaseModel):
    source_run: Optional[SourceRun] = None
    source_corrections: List[SummaryCorrection] = []
    target_run: Optional[TargetRun] = None
    target_details: Optional[Dict[str, Any]] = None

class ChatHistoryList(BaseModel):
    list: List[ChatHistoryItem] = []
    total_count: int
    total_pages: int
    page: int
    page_size: int


class ChatRoomHistoryList(ResponseBase):
    data: Optional[ChatHistoryList] = None


class ChatHistoryListSingle(BaseModel):
    # list: List[ChatHistoryItem] = []
    data: Optional[ChatHistoryItem] = None

class ChatRoomHistorySingle(BaseModel):
    data: Optional[ChatHistoryListSingle] = None
