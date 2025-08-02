# backend/routers/approval_router.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from schemas.approval_schemas import (
    ApprovalRequest, ApprovalResponse, ApprovalDecision,
    ApprovalListItem, ApprovalDetails, ApprovalStatistics
)
from agents.human_approval_agent import HumanApprovalAgent
from agents.audit_logger_agent import AuditLoggerAgent

router = APIRouter(prefix="/api/approval", tags=["approval"])

# Initialize agents
approval_agent = HumanApprovalAgent()
audit_logger = AuditLoggerAgent()

@router.post("/request", response_model=ApprovalResponse)
async def create_approval_request(request: ApprovalRequest):
    """Create a new approval request for a patch plan"""
    try:
        approval_id = approval_agent.create_approval_request(
            patch_plan=request.patch_plan,
            requester=request.requester
        )
        
        # Log the approval request creation
        audit_logger.log_user_action(
            user_id=request.requester,
            action="create_approval_request",
            resource_id=approval_id,
            details={"patch_plan_id": request.patch_plan.get("audit_id")}
        )
        
        approval_request = approval_agent.get_approval_request(approval_id)
        
        return ApprovalResponse(
            approval_id=approval_id,
            status="pending",
            created_at=approval_request["created_at"],
            message="Approval request created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create approval request: {str(e)}")

@router.get("/pending", response_model=List[ApprovalListItem])
async def get_pending_approvals():
    """Get all pending approval requests"""
    try:
        pending_approvals = approval_agent.list_pending_approvals()
        
        return [
            ApprovalListItem(
                approval_id=approval["approval_id"],
                patch_plan_id=approval["patch_plan_id"],
                created_at=approval["created_at"],
                status=approval["status"],
                requester=approval["requester"],
                total_patches=approval["approval_metadata"]["total_patches"],
                high_risk_count=approval["approval_metadata"]["high_risk_count"],
                compliance_frameworks=approval["approval_metadata"]["compliance_frameworks"],
                estimated_total_downtime=approval["approval_metadata"]["estimated_total_downtime"]
            )
            for approval in pending_approvals
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending approvals: {str(e)}")

@router.get("/{approval_id}", response_model=ApprovalDetails)
async def get_approval_details(approval_id: str):
    """Get detailed information about a specific approval request"""
    try:
        approval = approval_agent.get_approval_request(approval_id)
        
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        return ApprovalDetails(**approval)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get approval details: {str(e)}")

@router.post("/{approval_id}/decision")
async def make_approval_decision(approval_id: str, decision: ApprovalDecision):
    """Make a decision on an approval request"""
    try:
        # Get the approval request to validate it exists
        approval = approval_agent.get_approval_request(approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval request not found")
        
        # Update the approval status
        success = approval_agent.update_approval_status(
            approval_id=approval_id,
            status=decision.decision,
            approver=decision.approver,
            comments=decision.comments or ""
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update approval status")
        
        # Log the decision
        audit_logger.log_approval_decision(
            approval_id=approval_id,
            decision=decision.decision,
            approver=decision.approver,
            patch_plan_id=approval["patch_plan_id"],
            comments=decision.comments or "",
            additional_data={
                "total_patches": approval["approval_metadata"]["total_patches"],
                "high_risk_count": approval["approval_metadata"]["high_risk_count"]
            }
        )
        
        return {
            "message": f"Approval decision recorded: {decision.decision}",
            "approval_id": approval_id,
            "decision": decision.decision,
            "approver": decision.approver
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record decision: {str(e)}")

@router.get("/statistics/overview", response_model=ApprovalStatistics)
async def get_approval_statistics():
    """Get overview statistics for approval requests"""
    try:
        stats = approval_agent.get_approval_statistics()
        return ApprovalStatistics(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.get("/{approval_id}/audit-trail")
async def get_approval_audit_trail(approval_id: str):
    """Get complete audit trail for an approval request"""
    try:
        audit_trail = audit_logger.get_audit_trail(approval_id)
        
        return {
            "approval_id": approval_id,
            "audit_trail": audit_trail,
            "total_events": len(audit_trail)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit trail: {str(e)}")

@router.post("/{approval_id}/export-report")
async def export_approval_report(approval_id: str, format: str = "json"):
    """Export complete audit report for an approval request"""
    try:
        report_path = audit_logger.export_audit_report(approval_id, format)
        
        return {
            "message": "Audit report generated successfully",
            "report_path": report_path,
            "approval_id": approval_id,
            "format": format
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")