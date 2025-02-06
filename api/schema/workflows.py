from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Any

from datetime import datetime


class WorkflowsListData(BaseModel):
    workflows_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    icon_background: Optional[str] = None
    icon: Optional[str] = None
    publish_status: Optional[int] = None
    workflow_published_time: Optional[datetime] = None


class WorkflowsListResponseData(BaseModel):
    list: Optional[List[WorkflowsListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ResWorkflowsListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowsListResponseData] = None


class AppInfoData(BaseModel):
    app_id: Optional[int] = None
    user_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    enable_api: Optional[int] = None
    is_public: Optional[int] = None
    publish_status: Optional[int] = None
    created_time: Optional[datetime] = None
    status: Optional[int] = None
    api_url: Optional[str] = None


class WorkflowsInfoData(BaseModel):
    workflows_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    team_id: Optional[int] = None
    graph: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any] | str | int] = None


class WorkflowsInfoResponseData(BaseModel):
    app: Optional[AppInfoData] = None
    workflow: Optional[WorkflowsInfoData] = None


class ResWorkflowsInfoSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowsInfoResponseData] = None


class WorkflowsAppCreateResponseData(BaseModel):
    app_id: Optional[int] = None
    workflow_id: Optional[int] = None


class ResWorkflowsAppCreateSchem(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowsAppCreateResponseData] = None


class ReqWorkflowsAppCreateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[int] = None
    graph: Optional[Dict[str, Any]] = None
    # features: Optional[Dict[str, Any]] = None


class ReqWorkflowsAppUpdateSchema(BaseModel):
    # name: Optional[str] = None
    # description: Optional[str] = None
    is_public: Optional[int] = None
    enable_api: Optional[int] = None
    graph: Optional[Dict[str, Any]] = None
    # features: Optional[Dict[str, Any]] = None


class ResWorkflowsPublish(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[dict] = None


class WorkflowLogListData(BaseModel):
    workflows_id: Optional[int] = None
    user_id: Optional[int] = None
    app_id: Optional[int] = None
    name: Optional[str] = None
    app_runs_id: Optional[int] = None
    app_runs_name: Optional[str] = None
    app_runs_type: Optional[int] = None
    app_runs_level: Optional[int] = None
    elapsed_time: Optional[float] = None
    app_runs_status: Optional[int] = None
    completed_steps: Optional[int] = None
    total_steps: Optional[int] = None
    total_tokens: Optional[int] = None
    nickname: Optional[str] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None


class WorkflowLogListResponseData(BaseModel):
    list: Optional[List[WorkflowLogListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None


class ResWorkflowLogListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowLogListResponseData] = None


class NodeInputsDocument(BaseModel):
    inputs: Optional[Dict[str, Any]]
    context: Optional[List[Dict[str, Any]]]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "inputs": {
                        'input1': 'test',
                        'input2': 'test'
                    },
                    "context": {
                        'context1': 'test',
                        'context2': 'test'
                    },
                }
            ]
        }
    }


class ResWorkflowsNodeRun(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[dict] = None


class WorkflowsRunSchema(BaseModel):
    app_id: int
    run_type: int
    run_name: str
    inputs: dict
    knowledge_base_mapping: Optional[Dict[str, Any]] = None
    node_confirm_users: Dict[str, List[int]] = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "app_id": 1,
                    "run_type": 1,
                    "run_name": "1",
                    "inputs": {
                        "name": "node_input_var",
                        "type": "object",
                        "properties": {
                            "place": {
                                "name": "place",
                                "type": "string",
                                "value": ""
                            }
                        },
                        "display_name": "Input Object Variable"
                    },
                    "knowledge_base_mapping": {
                        "place": 1
                    },
                    "node_confirm_users": {
                        "exxfwqeq": [1, 2, 3],
                        "123213": [1, 2, 4],
                        "rrrrrrr": [1, 2, 3]
                    }
                }
            ]
        }
    }
    data_source_run_id: Optional[int] = 0


class WorkflowsNodeRunSchema(BaseModel):
    app_id: int
    node_id: str
    parent_node_id: Optional[str]
    inputs: Optional[Dict[str, Any]]
    context: Optional[List[Dict[str, Any]]]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "app_id": 1,
                    "node_id": "ddddddddddddd",
                    "inputs": {
                        "name": "node_input_var",
                        "type": "object",
                        "properties": {
                            "place": {
                                "name": "place",
                                "type": "string",
                                "value": ""
                            }
                        },
                        "display_name": "Input Object Variable"
                    },
                    "context": [
                        {
                            "level": 0,
                            "node_id": "27fcc88d-f918-4fd3-b18c-45268b52d5df",
                            "node_title": "",
                            "node_type": "start",
                            "output": {
                                "name": "output",
                                "type": "object",
                                "properties": {
                                    "33": {
                                        "name": "33",
                                        "type": "string",
                                        "value": "131313",
                                        "max_length": 0
                                    },
                                    "ccccc": {
                                        "name": "ccccc",
                                        "type": "string",
                                        "value": "3131313",
                                        "max_length": 0
                                    }
                                }
                            }
                        },
                        {
                            "level": 0,
                            "node_id": "6a4f86cc-6e04-49a0-8dfb-b23d986a59a8",
                            "node_title": "",
                            "node_type": "custom_code",
                            "output": {
                                "name": "output",
                                "type": "object",
                                "properties": {
                                    "32434243": {
                                        "name": "32434243",
                                        "type": "string",
                                        "value": "313313",
                                        "max_length": 0
                                    },
                                    "daddd": {
                                        "name": "daddd",
                                        "type": "string",
                                        "value": "133133",
                                        "max_length": 0
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
    }
    
class WorkflowStartConditionSchema(BaseModel):
    app_id: int
    workflow_id: int
    publish_status: int
    start_node: dict
    need_confirm_nodes: List[dict]
    
class ResWorkflowStartConditionSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowStartConditionSchema] = None

class WorkflowImportSchema(BaseModel):
    message: Optional[str] = None
    app_id: Optional[int] = None

class ResWorkflowImportSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowImportSchema] = None
    
class WorkflowCopySchema(BaseModel):
    message: Optional[str] = None
    app_id: Optional[int] = None

class ResWorkflowCopySchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[WorkflowCopySchema] = None
