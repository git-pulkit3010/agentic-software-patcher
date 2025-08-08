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
                 use_mongodb: bool = False):
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
                self.execution_collection = self.db["execution_logs"]
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
                "ip_address": "127.0.0.1",
                "session_id": str(uuid.uuid4())
            }
        }
        return self._save_log_entry(log_entry, "decision_log")

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
        return self._save_log_entry(log_entry, "generation_log")

    def log_patch_execution(self, execution_report: Dict) -> str:
        """Log patch execution results"""
        log_entry = {
            "log_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "event_type": "patch_execution",
            "patch_plan_id": execution_report.get("patch_plan_id", "unknown"),
            "execution_data": execution_report,
            "system_info": {
                "executor": "PatchExecutor",
                "platform": "WSL2" if "WSL2" in str(execution_report.get("system", "")) else "Unknown",
                "status": execution_report.get("status", "completed")
            }
        }
        return self._save_log_entry(log_entry, "execution_log")

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
        return self._save_log_entry(log_entry, "user_actions")

    def get_audit_trail(self, resource_id: str) -> List[Dict]:
        """Get complete audit trail for a resource"""
        audit_trail = []
        
        # Search file-based logs
        for log_file in self.audit_log_path.glob("audit_*.json"):
            with open(log_file, "r") as f:
                logs = json.load(f)
                for log in logs:
                    if (log.get("approval_id") == resource_id or 
                        log.get("patch_plan_id") == resource_id or
                        log.get("execution_data", {}).get("patch_plan_id") == resource_id):
                        audit_trail.append(log)
        
        # Search MongoDB if available
        if self.use_mongodb:
            try:
                mongo_logs = list(self.audit_collection.find({
                    "$or": [
                        {"approval_id": resource_id},
                        {"patch_plan_id": resource_id},
                        {"execution_data.patch_plan_id": resource_id}
                    ]
                }))
                
                for log in mongo_logs:
                    if "_id" in log:
                        log["_id"] = str(log["_id"])
                audit_trail.extend(mongo_logs)
            except Exception as e:
                print(f"[AuditLoggerAgent] MongoDB query failed: {e}")
        
        # Sort by timestamp
        audit_trail.sort(key=lambda x: x["timestamp"])
        return audit_trail

    def _save_log_entry(self, log_entry: Dict, log_type: str) -> str:
        """Unified method to save log entries"""
        # Save to file
        self._save_to_file(log_entry)
        
        # Save to MongoDB if available
        if self.use_mongodb:
            self._save_to_mongodb(log_entry, log_type)
        
        print(f"[AuditLoggerAgent] Logged {log_type} event: {log_entry['log_id']}")
        return log_entry["log_id"]

    def _save_to_file(self, log_entry: Dict):
        """Save log entry to file"""
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.audit_log_path / f"audit_{date_str}.json"
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    logs = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                logs = []
        
        logs.append(log_entry)
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)

    def _save_to_mongodb(self, log_entry: Dict, collection_type: str):
        """Save log entry to MongoDB"""
        try:
            if collection_type == "decision_log":
                self.decision_collection.insert_one(log_entry)
            elif collection_type == "generation_log":
                self.audit_collection.insert_one(log_entry)
            elif collection_type == "execution_log":
                self.execution_collection.insert_one(log_entry)
            else:
                self.audit_collection.insert_one(log_entry)
        except Exception as e:
            print(f"[AuditLoggerAgent] MongoDB save failed: {e}")

    # ... (keep existing get_decision_statistics and export_audit_report methods) ...