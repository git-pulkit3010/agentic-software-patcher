# backend/agents/auditor.py

import json
import uuid
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

class AuditorAgent:
    def __init__(self, audit_log_path: str = "backend/data/audit_logs"):
        self.audit_log_path = Path(audit_log_path)
        self.audit_log_path.mkdir(parents=True, exist_ok=True)
        
        # Mock compliance frameworks
        self.compliance_frameworks = {
            "PCI-DSS": {
                "requirements": ["vulnerability_management", "regular_testing", "access_controls"],
                "patch_timeline": "within_30_days",
                "documentation_required": True
            },
            "HIPAA": {
                "requirements": ["security_risk_assessment", "assigned_security_responsibility"], 
                "patch_timeline": "within_60_days",
                "documentation_required": True
            },
            "SOX": {
                "requirements": ["change_management", "access_controls", "monitoring"],
                "patch_timeline": "within_90_days", 
                "documentation_required": True
            },
            "ISO27001": {
                "requirements": ["vulnerability_management", "incident_response"],
                "patch_timeline": "risk_based",
                "documentation_required": True
            }
        }
    
    def tag_compliance_requirements(self, scheduled_patches: List[Dict]) -> List[Dict]:
        """Tag each scheduled patch with relevant compliance requirements"""
        tagged_patches = []
        
        for patch in scheduled_patches:
            # Determine applicable compliance frameworks based on system type and criticality
            applicable_frameworks = self._determine_compliance_frameworks(patch)
            
            # Add compliance metadata
            compliance_metadata = {
                "applicable_frameworks": applicable_frameworks,
                "compliance_requirements": self._get_requirements_for_frameworks(applicable_frameworks),
                "documentation_needed": any(self.compliance_frameworks[fw]["documentation_required"] 
                                          for fw in applicable_frameworks),
                "max_timeline": self._get_strictest_timeline(applicable_frameworks)
            }
            
            tagged_patch = {
                **patch,  # Copy all existing patch data
                "compliance_metadata": compliance_metadata,
                "audit_trail": {
                    "created_at": datetime.now().isoformat(),
                    "audit_id": str(uuid.uuid4()),
                    "tagged_by": "AuditorAgent",
                    "version": "1.0"
                }
            }
            
            tagged_patches.append(tagged_patch)
        
        return tagged_patches
    
    def _determine_compliance_frameworks(self, patch: Dict) -> List[str]:
        """Determine which compliance frameworks apply to this patch"""
        frameworks = []
        
        system = patch.get("target_system", {})
        severity = patch.get("severity", "low")
        system_type = system.get("type", "")
        environment = system.get("environment", "")
        
        # Business logic for compliance applicability (mock for PoC)
        if system_type == "database" or "user_data" in system.get("affected_services", []):
            frameworks.extend(["PCI-DSS", "HIPAA"])
        
        if environment == "production":
            frameworks.append("SOX")
            
        if patch.get("risk_score", 0) >= 70:
            frameworks.append("ISO27001")
            
        # Remove duplicates
        return list(set(frameworks))
    
    def _get_requirements_for_frameworks(self, frameworks: List[str]) -> List[str]:
        """Get all requirements from applicable frameworks"""
        all_requirements = []
        for framework in frameworks:
            if framework in self.compliance_frameworks:
                all_requirements.extend(self.compliance_frameworks[framework]["requirements"])
        return list(set(all_requirements))  # Remove duplicates
    
    def _get_strictest_timeline(self, frameworks: List[str]) -> str:
        """Get the most restrictive timeline from applicable frameworks"""
        timeline_priority = {
            "within_30_days": 1,
            "within_60_days": 2, 
            "within_90_days": 3,
            "risk_based": 4
        }
        
        strictest = "risk_based"  # Default
        strictest_priority = 99
        
        for framework in frameworks:
            if framework in self.compliance_frameworks:
                timeline = self.compliance_frameworks[framework]["patch_timeline"]
                priority = timeline_priority.get(timeline, 99)
                if priority < strictest_priority:
                    strictest = timeline
                    strictest_priority = priority
                    
        return strictest
    
    def log_audit_entry(self, patch_plan: Dict, action: str = "patch_plan_generated") -> str:
        """Log audit entry for compliance tracking"""
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "patch_plan_summary": {
                "total_patches": len(patch_plan.get("scheduled_patches", [])),
                "high_risk_patches": len([p for p in patch_plan.get("scheduled_patches", []) 
                                        if p.get("risk_score", 0) >= 70]),
                "compliance_frameworks": list(set([
                    fw for patch in patch_plan.get("scheduled_patches", [])
                    for fw in patch.get("compliance_metadata", {}).get("applicable_frameworks", [])
                ]))
            },
            "system_impact": self._calculate_system_impact(patch_plan),
            "compliance_status": "pending_approval"
        }
        
        # Save to audit log file
        audit_file = self.audit_log_path / f"audit_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Load existing entries or create new
        audit_log = []
        if audit_file.exists():
            with open(audit_file, "r") as f:
                audit_log = json.load(f)
        
        audit_log.append(audit_entry)
        
        with open(audit_file, "w") as f:
            json.dump(audit_log, f, indent=2)
            
        print(f"[AuditorAgent] Logged audit entry: {audit_entry['audit_id']}")
        return audit_entry["audit_id"]
    
    def _calculate_system_impact(self, patch_plan: Dict) -> Dict:
        """Calculate the impact across systems"""
        scheduled_patches = patch_plan.get("scheduled_patches", [])
        
        # Count systems by environment and criticality
        environments = {}
        criticalities = {}
        
        for patch in scheduled_patches:
            system = patch.get("target_system", {})
            env = system.get("environment", "unknown")
            crit = system.get("criticality", "unknown")
            
            environments[env] = environments.get(env, 0) + 1
            criticalities[crit] = criticalities.get(crit, 0) + 1
        
        return {
            "environments_affected": environments,
            "criticality_levels": criticalities,
            "total_systems": len(set(patch.get("target_system", {}).get("id", "") 
                                   for patch in scheduled_patches))
        }
    
    def run(self, scheduled_patches: List[Dict]) -> Dict:
        """Main method to add audit metadata and log"""
        print("[AuditorAgent] Tagging compliance requirements...")
        tagged_patches = self.tag_compliance_requirements(scheduled_patches)
        
        # Create comprehensive patch plan with audit data
        patch_plan = {
            "scheduled_patches": tagged_patches,
            "plan_metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_patches": len(tagged_patches),
                "compliance_summary": self._generate_compliance_summary(tagged_patches)
            }
        }
        
        # Log audit entry
        audit_id = self.log_audit_entry(patch_plan)
        patch_plan["audit_id"] = audit_id
        
        return patch_plan
    
    def _generate_compliance_summary(self, patches: List[Dict]) -> Dict:
        """Generate high-level compliance summary"""
        all_frameworks = []
        documentation_needed = 0
        
        for patch in patches:
            compliance = patch.get("compliance_metadata", {})
            all_frameworks.extend(compliance.get("applicable_frameworks", []))
            if compliance.get("documentation_needed", False):
                documentation_needed += 1
        
        return {
            "frameworks_involved": list(set(all_frameworks)),
            "patches_requiring_documentation": documentation_needed,
            "total_compliance_requirements": len(set(all_frameworks))
        }
