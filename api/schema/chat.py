from pydantic import BaseModel
from typing import Optional, List, Any, Dict, Literal

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
    icon: Optional[str] = None
    icon_background: Optional[str] = None


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

class ChatRoomDetailResponse(ResponseBase):
    data: Optional[ChatRoomDetailInfo] = None

class ChatRoomResponseBase(ResponseBase):
    data: Dict[str, Any]


class ToggleSmartSelectionSwitch(BaseModel):
    smart_selection: Literal[0, 1]

