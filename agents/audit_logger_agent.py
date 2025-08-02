# backend/agents/audit_logger_agent.py

import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from pymongo import MongoClient
import os

class AuditLoggerAgent:
    def __init__(self, 
                 audit_log_path: str = "backend/data/audit_logs",
                 use_mongodb: bool = True):
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.mkdir(parents=True, exist_ok=True)
        self.use_mongodb = use_mongodb
        
        # MongoDB setup
        if use_mongodb:
            try:
                self.client = MongoClient("mongodb://localhost:27017/")
                self.db = self.client["patch_management"]
                self.audit_collection = self.db["audit_logs"]
                self.decision_collection = self.db["approval_decisions"]
            except Exception as e:
                print(f"[AuditLoggerAgent] MongoDB connection failed: {e}")
                self.use_mongodb = False
    
    def log_approval_decision(self, 
                            approval_id: str,
                            decision: str,
                            approver: str,
                            patch_plan_id: str,
                            comments: str = "",
                            additional_data: Dict = None) -> str:
        """Log an approval decision with full audit trail"""
        
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": "approval_decision",
            "approval_id": approval_id,
            "patch_plan_id": patch_plan_id,
            "decision": decision,
            "approver": approver,
            "comments": comments,
            "additional_data": additional_data or {},
            "system_info": {
                "user_agent": "PatchManagementSystem",
                "ip_address": "127.0.0.1",  # In real implementation, get actual IP
                "session_id": str(uuid.uuid4())
            }
        }
        
        # Save to file
        self._save_to_file(log_entry)
        
        # Save to MongoDB if available
        if self.use_mongodb:
            self._save_to_mongodb(log_entry, "decision_log")
        
        print(f"[AuditLoggerAgent] Logged approval decision: {decision} for {approval_id}")
        return log_entry["log_id"]
    
    def log_patch_plan_generation(self, patch_plan: Dict[str, Any]) -> str:
        """Log patch plan generation event"""
        
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": "patch_plan_generated",
            "patch_plan_id": patch_plan.get("audit_id", "unknown"),
            "metadata": {
                "total_patches": len(patch_plan.get("scheduled_patches", [])),
                "high_risk_count": len([p for p in patch_plan.get("scheduled_patches", [])
                                      if p.get("risk_score", 0) >= 70]),
                "compliance_frameworks": patch_plan.get("plan_metadata", {})
                    .get("compliance_summary", {}).get("frameworks_involved", []),
                "generation_method": "automated_llm_assisted"
            },
            "system_info": {
                "generator": "PatchPlanGenerator",
                "version": "3.0",
                "llm_enabled": True
            }
        }
        
        self._save_to_file(log_entry)
        
        if self.use_mongodb:
            self._save_to_mongodb(log_entry, "generation_log")
        
        print(f"[AuditLoggerAgent] Logged patch plan generation: {patch_plan.get('audit_id')}")
        return log_entry["log_id"]
    
    def log_user_action(self, 
                       user_id: str,
                       action: str, 
                       resource_id: str,
                       details: Dict = None) -> str:
        """Log user actions for audit trail"""
        
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": "user_action",
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id,
            "details": details or {},
            "system_info": {
                "component": "ApprovalUI",
                "session_timestamp": datetime.now().isoformat()
            }
        }
        
        self._save_to_file(log_entry)
        
        if self.use_mongodb:
            self._save_to_mongodb(log_entry, "user_actions")
        
        return log_entry["log_id"]
    
    def get_audit_trail(self, resource_id: str) -> List[Dict]:
        """Get complete audit trail for a resource"""
        audit_trail = []
        
        # Search file-based logs
        for log_file in self.audit_log_path.glob("audit_*.json"):
            with open(log_file, "r") as f:
                logs = json.load(f)
                for log in logs:
                    if (log.get("approval_id") == resource_id or 
                        log.get("patch_plan_id") == resource_id):
                        audit_trail.append(log)
        
        # Search MongoDB if available
        if self.use_mongodb:
            try:
                mongo_logs = list(self.audit_collection.find({
                    "$or": [
                        {"approval_id": resource_id},
                        {"patch_plan_id": resource_id},
                        {"resource_id": resource_id}
                    ]
                }))
                
                # Convert MongoDB ObjectId to string
                for log in mongo_logs:
                    if "_id" in log:
                        log["_id"] = str(log["_id"])
                        
                audit_trail.extend(mongo_logs)
            except Exception as e:
                print(f"[AuditLoggerAgent] MongoDB query failed: {e}")
        
        # Sort by timestamp
        audit_trail.sort(key=lambda x: x["timestamp"])
        return audit_trail
    
    def get_decision_statistics(self, date_range: int = 30) -> Dict:
        """Get approval decision statistics for the last N days"""
        
        stats = {
            "total_decisions": 0,
            "approved": 0,
            "rejected": 0,
            "changes_requested": 0,
            "pending": 0,
            "decisions_by_user": {},
            "decisions_by_day": {}
        }
        
        # Calculate cutoff date
        cutoff_date = datetime.now().replace(day=max(1, datetime.now().day - date_range))
        
        # Analyze file-based logs
        for log_file in self.audit_log_path.glob("audit_*.json"):
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
                    for log in logs:
                        if (log.get("event_type") == "approval_decision" and
                            datetime.fromisoformat(log["timestamp"]) >= cutoff_date):
                            
                            stats["total_decisions"] += 1
                            decision = log.get("decision", "unknown")
                            
                            if decision in stats:
                                stats[decision] += 1
                            
                            # Count by user
                            approver = log.get("approver", "unknown")
                            stats["decisions_by_user"][approver] = \
                                stats["decisions_by_user"].get(approver, 0) + 1
                            
                            # Count by day
                            day = log["timestamp"][:10]  # YYYY-MM-DD
                            stats["decisions_by_day"][day] = \
                                stats["decisions_by_day"].get(day, 0) + 1
            except Exception as e:
                print(f"[AuditLoggerAgent] Error processing log file {log_file}: {e}")
        
        return stats
    
    def _save_to_file(self, log_entry: Dict):
        """Save log entry to file"""
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.audit_log_path / f"audit_{date_str}.json"
        
        # Load existing logs or create new
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
        
        logs.append(log_entry)
        
        # Save updated logs
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
    
    def _save_to_mongodb(self, log_entry: Dict, collection_type: str):
        """Save log entry to MongoDB"""
        try:
            if collection_type == "decision_log":
                self.decision_collection.insert_one(log_entry)
            else:
                self.audit_collection.insert_one(log_entry)
        except Exception as e:
            print(f"[AuditLoggerAgent] MongoDB save failed: {e}")
    
    def export_audit_report(self, resource_id: str, format: str = "json") -> str:
        """Export complete audit report for a resource"""
        
        audit_trail = self.get_audit_trail(resource_id)
        
        if format.lower() == "json":
            report_file = self.audit_log_path / f"audit_report_{resource_id}_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, "w") as f:
                json.dump({
                    "resource_id": resource_id,
                    "generated_at": datetime.now().isoformat(),
                    "audit_trail": audit_trail,
                    "summary": {
                        "total_events": len(audit_trail),
                        "event_types": list(set(log.get("event_type", "unknown") for log in audit_trail)),
                        "date_range": {
                            "start": min(log["timestamp"] for log in audit_trail) if audit_trail else None,
                            "end": max(log["timestamp"] for log in audit_trail) if audit_trail else None
                        }
                    }
                }, f, indent=2)
            
            return str(report_file)
        
        return "Format not supported"