from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NodeData(BaseModel):
    exec_id: Optional[int] = None
    workflow_id: Optional[int] = None
    exec_user_id: Optional[int] = None
    app_run_id: Optional[int] = None
    type: Optional[int] = None
    level: Optional[int] = None
    edge_id: Optional[str] = None
    pre_node_id: Optional[str] = None
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    node_name: Optional[str] = None
    node_graph: Optional[Dict[str, Any]] = None
    inputs: Optional[Dict[str, Any]] = None
    correct_prompt: Optional[Dict[str, Any]] = None
    correct_llm_history: Optional[List[Dict[str, Any]]] = None
    prompt_data: Optional[List] = None
    status: Optional[int] = None
    error: Optional[str] = None
    condition_id: Optional[str] = None
    outputs: Optional[Dict[str, Any]] = None
    output_type: Optional[int] = None
    elapsed_time: Optional[float] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    embedding_tokens: Optional[int] = None
    reranking_tokens: Optional[int] = None
    created_time: Optional[datetime] = None
    updated_time: Optional[datetime] = None
    finished_time: Optional[datetime] = None
    need_human_confirm: Optional[int] = None
    completed_steps: Optional[int] = None
    app_run_status: Optional[int] = None
    app_run_level: Optional[int] = None
    completed_edges: Optional[list] = None
    context: Optional[list] = None



class ResNodeInfoSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[NodeData] = None

class BackListData(BaseModel):
    app_run_id: Optional[int] = None
    app_run_name: Optional[str] = None
    app_name: Optional[str] = None
    mode: Optional[int] = None
    node_id: Optional[str] = None
    node_name: Optional[str] = None
    exec_id: Optional[int] = None
    need_human_confirm: Optional[int] = None
    icon: Optional[str] = None
    icon_background: Optional[str] = None

class BackListResponseData(BaseModel):
    list: Optional[List[BackListData]] = None
    total_count: Optional[int] = None
    total_pages: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

class ResBackListSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[BackListResponseData] = None

class ReqNodeUpdateSchema(BaseModel):
    operation: Optional[int] = None
    inputs: Optional[Dict[str, Any]] = None
    knowledge_base_mapping: Optional[Dict[str, Any]] = None
    outputs: Optional[Dict[str, Any]] = None
    correct_prompt: Optional[Dict[str, Any]] = None

class NodeUpdateResponseData(BaseModel):
    exec_id: Optional[int] = None

class ResNodeUpdateSchema(BaseModel):
    code: Optional[int] = None
    detail: Optional[str] = None
    data: Optional[NodeUpdateResponseData] = None
