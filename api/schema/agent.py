from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union

class AgentListData(BaseModel):
    agent_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None

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

class ReqAgentBaseCreateSchema(BaseModel):
    is_public: Optional[int] = None
    attrs_are_visible: Optional[int] = None
    enable_api: Optional[int] = None
    obligations: Optional[str] = None
    input_variables: Optional[Dict[str, Any]] = None
    dataset_ids: Optional[List[int]] = None
    m_config_id: Optional[int] = None
    allow_upload_file: Optional[int] = None
    default_output_format: Optional[int] = None

class AgentBaseCreateResponseData(BaseModel):
    """Response schema for agent creation"""
    app_id: int

class ResAgentBaseCreateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentBaseCreateResponseData] = None

class AgentAbilitiesData(BaseModel):
    agent_ability_id: Optional[int] = None
    name: Optional[str] = None
    content: Optional[str] = None
    status: Optional[int] = None
    output_format: Optional[int] = None

class ReqAgentAbilitiesSetSchema(BaseModel):
    auto_match_ability: Optional[int] = None
    agent_abilities: Optional[List[AgentAbilitiesData]] = None

class AbilitiesOutputFormatData(BaseModel):
    agent_ability_id: Optional[int] = None
    output_format: Optional[int] = None

class ReqAgentOutputSetSchema(BaseModel):
    default_output_format: Optional[int] = None
    abilities_output_format_data: Optional[List[AbilitiesOutputFormatData]] = None

class ReqAgentEngineSetSchema(BaseModel):
    m_config_id: Optional[int] = None
    allow_upload_file: Optional[int] = None

class AgentInfoAppResponseData(BaseModel):
    app_id: Optional[int] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None
    is_public: Optional[int] = None
    attrs_are_visible: Optional[int] = None
    enable_api: Optional[int] = None
    publish_status: Optional[int] = None
    created_time: Optional[datetime] = None
    status: Optional[int] = None
    api_url: Optional[str] = None

class AgentInfoAgentResponseData(BaseModel):
    agent_id: Optional[int] = None
    user_id: Optional[int] = None
    obligations: Optional[str] = None
    input_variables: Optional[Dict[str, Any]] = None
    auto_match_ability: Optional[int] = None
    default_output_format: Optional[int] = None
    m_config_id: Optional[int] = None
    allow_upload_file: Optional[int] = None
    publish_status: Optional[int] = None
    published_time: Optional[Union[datetime, None]] = None
    created_time: Optional[datetime] = None
    status: Optional[int] = None

class AgentInfoDatasetData(BaseModel):
    dataset_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None

class AgentInfoAbilitiesData(BaseModel):
    agent_ability_id: Optional[int] = None
    name: Optional[str] = None
    content: Optional[str] = None
    output_format: Optional[int] = None
    status: Optional[int] = None

class AgentInfoConfigurationsData(BaseModel):
    m_config_id: Optional[int] = None
    m_id: Optional[int] = None
    m_name: Optional[str] = None
    supplier_id: Optional[int] = None
    supplier_name: Optional[str] = None

class AgentInfoResponseData(BaseModel):
    app: Optional[AgentInfoAppResponseData] = None
    agent: Optional[AgentInfoAgentResponseData] = None
    agent_dataset_relation_list: Optional[List[AgentInfoDatasetData]] = None
    agent_abilities_list: Optional[List[AgentInfoAbilitiesData]] = None
    m_configurations_list: Optional[List[AgentInfoConfigurationsData]] = None
    is_creator: Optional[int] = None
    creator_nickname: Optional[str] = None

class ResAgentInfoSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentInfoResponseData] = None

class ReqAgentRunSchema(BaseModel):
    agent_id: Optional[int] = None
    ability_id: Optional[int] = None
    input_dict: Optional[Dict[str, Any]] = None
    prompt: Optional[Dict[str, Any]] = None
    data_source_run_id: Optional[int] = 0

class AgentRunResponseData(BaseModel):
    outputs: Optional[Dict[str, Any]] = None
    outputs_md: Optional[str] = None

class ResAgentRunSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentRunResponseData] = None

class ReqAgentGenerateSchema(BaseModel):
    user_prompt: Optional[str] = None

class AgentGenerateResonseData(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None

class ResAgentGenerateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentGenerateResonseData] = None


class ReqAgentRegenerateSchema(BaseModel):
    app_run_id: Optional[int] = None

class ReqAgentSupplementSchema(BaseModel):
    app_run_id: Optional[int] = None
    supplement_prompt: Optional[str] = None


class ReqAgentBatchSample(BaseModel):
    app_run_id: Optional[int] = None
    supplement_prompt: Optional[str] = None

class AgentBatchGenerateResonseData(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None

class ResAgentBatchSample(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentBatchGenerateResonseData] = None

class ReqAgentSaveSchema(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None
    agent_info: Optional[Dict[str, Any]] = Field(
        {
            "name": "text",
            "type": "json",
            "value": {
                "name":"Agent 1",
                "description":"Agent 1 description",
                "obligations":"Agent 1 obligations",
                "abilities":[
                    {
                        "name":"ability1",
                        "content":"ability content",
                        "output_format":0
                    }
                ]
            }
        }
    )

class AgentSaveResponseData(BaseModel):
    app_run_id: Optional[int] = None
    record_id: Optional[int] = None

class ResAgentSaveSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentSaveResponseData] = None

class ReqAgentBatchGenerateSchema(BaseModel):
    app_run_id: Optional[int] = None
    loop_count: Optional[int] = 10              # Number of agents per batch
    loop_limit: Optional[int] = None      # Total agents to generate
    supplement_prompt: Optional[str] = None
    loop_id: Optional[int] = 0                       # Loop iteration ID

class AgentBatchGenerateResonseData(BaseModel):
    app_run_id: Optional[int] = None
    loop_id: Optional[int] = None


class ResAgentBatchGenerateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[AgentBatchGenerateResonseData] = None


class AgentConfigData(BaseModel):
    """Schema for individual agent configuration"""  
    app_id: Optional[int] = Field(
        None, 
        description="App ID for updating existing agent. If not provided, creates new agent"
    )
    name: str
    description: str
    obligations: str 
    abilities: List[Dict[str, Any]]
    tags: Optional[List[int]] = []

class ReqAgentBatchCreateSchema(BaseModel):
    """Schema for batch agent creation/update request"""
    agents: List[AgentConfigData] = Field(
        ...,
        description="List of agent configurations. Each can be create or update based on app_id"
    )

class ResBatchAgentCreateSchema(BaseModel):
    """Response schema for batch agent creation"""
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Dict[str, List[int]] = Field(
        ...,
        description="Contains list of created app IDs",
        example={"app_ids": [1, 2, 3]}
    )


class AgentResponseBase(BaseModel):
    data: Dict[str, Any]


class AgentLogListResponse(BaseModel):
    data: Dict[str, Any]


class AgentLogDetailResponse(BaseModel):
    data: Dict[str, Any]