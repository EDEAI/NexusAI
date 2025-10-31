from typing import Any, Optional, Dict
from pydantic import BaseModel


class TeamCreateRequest(BaseModel):
    """Team creation request schema"""
    name: str
    account: str
    password: str
    config: Optional[Dict[str, Any]] = None


class TeamUpdateRequest(BaseModel):
    """Team update request schema"""
    team_id: int
    name: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class TeamStatusUpdateRequest(BaseModel):
    """Team status update request schema"""
    team_id: int
    status: int
