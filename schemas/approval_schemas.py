# backend/schemas/approval_schemas.py

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"

class ApprovalDecision(BaseModel):
    #approval_id: str = Field(..., description="Unique approval request ID")
    decision: ApprovalStatus = Field(..., description="Approval decision")
    approver: str = Field(..., description="Person making the decision")
    comments: Optional[str] = Field(None, description="Comments about the decision")
    
class ApprovalRequest(BaseModel):
    patch_plan: Dict[str, Any] = Field(..., description="Complete patch plan")
    requester: str = Field(default="system", description="Who requested approval")

class ApprovalResponse(BaseModel):
    approval_id: str = Field(..., description="Generated approval ID")
    status: ApprovalStatus = Field(..., description="Current approval status")
    created_at: str = Field(..., description="Creation timestamp")
    message: str = Field(..., description="Response message")

class ApprovalListItem(BaseModel):
    approval_id: str
    patch_plan_id: str
    created_at: str
    status: ApprovalStatus
    requester: str
    total_patches: int
    high_risk_count: int
    compliance_frameworks: List[str]
    estimated_total_downtime: str

class ApprovalDetails(BaseModel):
    approval_id: str
    patch_plan_id: str
    created_at: str
    status: ApprovalStatus
    requester: str
    patch_plan: Dict[str, Any]
    approval_metadata: Dict[str, Any]
    comments: List[Dict[str, Any]]
    decision_history: List[Dict[str, Any]]

class ApprovalStatistics(BaseModel):
    total_requests: int
    pending: int
    approved: int
    rejected: int
    changes_requested: int