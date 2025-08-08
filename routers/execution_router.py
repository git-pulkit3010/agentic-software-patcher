# backend/routers/execution_router.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from agents.patch_executor import PatchExecutor
from agents.audit_logger_agent import AuditLoggerAgent
from agents.human_approval_agent import HumanApprovalAgent
import json
import os

router = APIRouter(prefix="/api/execute", tags=["execution"])
executor = PatchExecutor()
audit_logger = AuditLoggerAgent()
approval_agent = HumanApprovalAgent()

class ExecuteRequest(BaseModel):
    approval_id: str

@router.post("/")
async def execute_approved_plan(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """Execute patches for an approved plan"""
    try:
        # 1. Validate approval exists and is approved
        approval = approval_agent.get_approval_request(request.approval_id)
        if not approval:
            raise HTTPException(status_code=404, detail="Approval not found")
        if approval["status"] != "approved":
            raise HTTPException(status_code=409, detail="Plan not approved")

        # 2. Get patch plan
        patch_plan = approval["patch_plan"]
        
        # 3. Execute in background (non-blocking)
        background_tasks.add_task(run_patches, request.approval_id, patch_plan)
        
        return {
            "message": "Execution started",
            "approval_id": request.approval_id,
            "log_file": f"backend/data/execution_logs/{request.approval_id}.log"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run_patches(approval_id: str, patch_plan: dict):
    """Actual execution logic"""
    try:
        # Log start
        audit_logger.log_user_action(
            user_id="system",
            action="patch_execution_started",
            resource_id=approval_id
        )
        
        # Execute patches
        results = executor.execute(patch_plan)
        
        # Log completion
        execution_report = {
            "approval_id": approval_id,
            "results": results,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        audit_logger.log_patch_execution(execution_report)
        
        # Save results
        os.makedirs("backend/data/execution_logs", exist_ok=True)
        with open(f"backend/data/execution_logs/{approval_id}.json", "w") as f:
            json.dump(execution_report, f, indent=2)
            
    except Exception as e:
        # Log failure
        audit_logger.log_user_action(
            user_id="system",
            action="patch_execution_failed",
            resource_id=approval_id,
            details={"error": str(e)}
        )