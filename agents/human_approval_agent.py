# backend/agents/human_approval_agent.py

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from enum import Enum

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved" 
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"

class HumanApprovalAgent:
    def __init__(self, approval_store_path: str = "backend/data/approvals"):
        self.approval_store_path = Path(approval_store_path)
        self.approval_store_path.mkdir(parents=True, exist_ok=True)
        
    def create_approval_request(self, patch_plan: Dict[str, Any], requester: str = "system") -> str:
        """Create a new approval request for a patch plan"""
        approval_id = str(uuid.uuid4())
        
        approval_request = {
            "approval_id": approval_id,
            "patch_plan_id": patch_plan.get("audit_id", "unknown"),
            "created_at": datetime.now().isoformat(),
            "requester": requester,
            "status": ApprovalStatus.PENDING.value,
            "patch_plan": patch_plan,
            "approval_metadata": {
                "total_patches": len(patch_plan.get("scheduled_patches", [])),
                "high_risk_count": len([p for p in patch_plan.get("scheduled_patches", []) 
                                      if p.get("risk_score", 0) >= 70]),
                "compliance_frameworks": patch_plan.get("plan_metadata", {})
                    .get("compliance_summary", {}).get("frameworks_involved", []),
                "estimated_total_downtime": self._calculate_total_downtime(patch_plan)
            },
            "comments": [],
            "decision_history": []
        }
        
        # Save to file
        approval_file = self.approval_store_path / f"approval_{approval_id}.json"
        with open(approval_file, "w") as f:
            json.dump(approval_request, f, indent=2)
            
        print(f"[HumanApprovalAgent] Created approval request: {approval_id}")
        return approval_id
    
    def get_approval_request(self, approval_id: str) -> Optional[Dict]:
        """Retrieve an approval request by ID"""
        approval_file = self.approval_store_path / f"approval_{approval_id}.json"
        if not approval_file.exists():
            return None
            
        with open(approval_file, "r") as f:
            return json.load(f)
    
    def list_pending_approvals(self) -> List[Dict]:
        """Get all pending approval requests"""
        pending_approvals = []
        
        for approval_file in self.approval_store_path.glob("approval_*.json"):
            with open(approval_file, "r") as f:
                approval = json.load(f)
                if approval.get("status") == ApprovalStatus.PENDING.value:
                    pending_approvals.append(approval)
        
        # Sort by creation date (newest first)
        pending_approvals.sort(key=lambda x: x["created_at"], reverse=True)
        return pending_approvals
    
    def update_approval_status(self, approval_id: str, status: str, 
                             approver: str, comments: str = "") -> bool:
        """Update the status of an approval request"""
        approval_file = self.approval_store_path / f"approval_{approval_id}.json"
        if not approval_file.exists():
            return False
            
        with open(approval_file, "r") as f:
            approval = json.load(f)
        
        # Add decision to history
        decision = {
            "timestamp": datetime.now().isoformat(),
            "approver": approver,
            "previous_status": approval["status"],
            "new_status": status,
            "comments": comments
        }
        
        approval["decision_history"].append(decision)
        approval["status"] = status
        approval["last_updated"] = datetime.now().isoformat()
        
        if comments:
            comment_entry = {
                "timestamp": datetime.now().isoformat(),
                "author": approver,
                "comment": comments,
                "action": status
            }
            approval["comments"].append(comment_entry)
        
        # Save updated approval
        with open(approval_file, "w") as f:
            json.dump(approval, f, indent=2)
            
        print(f"[HumanApprovalAgent] Updated approval {approval_id}: {status}")
        return True
    
    def _calculate_total_downtime(self, patch_plan: Dict) -> str:
        """Calculate estimated total downtime from all patches"""
        scheduled_patches = patch_plan.get("scheduled_patches", [])
        total_minutes = 0
        
        for patch in scheduled_patches:
            duration_str = patch.get("estimated_duration", "30 minutes")
            # Extract minutes from duration string (simplified parsing)
            if "hour" in duration_str:
                hours = float(duration_str.split()[0].split("-")[0])
                total_minutes += hours * 60
            elif "minute" in duration_str:
                minutes = float(duration_str.split()[0].split("-")[0])
                total_minutes += minutes
        
        if total_minutes >= 60:
            hours = total_minutes / 60
            return f"{hours:.1f} hours"
        else:
            return f"{int(total_minutes)} minutes"
    
    def get_approval_statistics(self) -> Dict:
        """Get statistics about approval requests"""
        stats = {
            "total_requests": 0,
            "pending": 0,
            "approved": 0,
            "rejected": 0,
            "changes_requested": 0
        }
        
        for approval_file in self.approval_store_path.glob("approval_*.json"):
            with open(approval_file, "r") as f:
                approval = json.load(f)
                stats["total_requests"] += 1
                status = approval.get("status", "unknown")
                if status in stats:
                    stats[status] += 1
        
        return stats