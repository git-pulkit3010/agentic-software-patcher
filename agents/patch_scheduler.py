# backend/agents/patch_scheduler.py

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

class PatchSchedulerAgent:
    def __init__(self, systems_file_path: str = "backend/data/mock_systems.json"):
        self.systems_file_path = Path(systems_file_path)
        self.systems = self._load_systems()
        
    def _load_systems(self):
        """Load mock systems inventory"""
        if not self.systems_file_path.exists():
            # Create default systems if file doesn't exist
            default_systems = self._create_default_systems()
            self.systems_file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.systems_file_path, "w") as f:
                json.dump(default_systems, f, indent=2)
            return default_systems
        
        with open(self.systems_file_path, "r") as f:
            return json.load(f)
    
    def _create_default_systems(self):
        """Create default mock systems for PoC"""
        return {
            "systems": [
                {
                    "id": "SYS-001",
                    "name": "Web Server Cluster",
                    "type": "web_server",
                    "environment": "production",
                    "criticality": "high",
                    "maintenance_window": {
                        "day": "sunday",
                        "start_time": "02:00",
                        "end_time": "06:00",
                        "timezone": "UTC"
                    },
                    "affected_services": ["web_frontend", "api_gateway"]
                },
                {
                    "id": "SYS-002", 
                    "name": "Database Primary",
                    "type": "database",
                    "environment": "production",
                    "criticality": "critical",
                    "maintenance_window": {
                        "day": "saturday",
                        "start_time": "01:00",
                        "end_time": "04:00",
                        "timezone": "UTC"
                    },
                    "affected_services": ["user_data", "transactions"]
                },
                {
                    "id": "SYS-003",
                    "name": "Development Servers",
                    "type": "development",
                    "environment": "development", 
                    "criticality": "low",
                    "maintenance_window": {
                        "day": "any",
                        "start_time": "00:00",
                        "end_time": "23:59",
                        "timezone": "UTC"
                    },
                    "affected_services": ["dev_testing"]
                },
                {
                    "id": "SYS-004",
                    "name": "Staging Environment",
                    "type": "staging",
                    "environment": "staging",
                    "criticality": "medium",
                    "maintenance_window": {
                        "day": "weekdays",
                        "start_time": "18:00", 
                        "end_time": "08:00",
                        "timezone": "UTC"
                    },
                    "affected_services": ["staging_tests", "qa_validation"]
                }
            ]
        }
    
    def map_patches_to_systems(self, patch_risks: List[Dict]) -> List[Dict]:
        """Map each patch to appropriate systems based on risk and criticality"""
        scheduled_patches = []
        
        for patch_risk in patch_risks:
            # Simple logic: higher risk patches go to less critical systems first
            risk_score = patch_risk.get("risk_score", 0)
            severity = patch_risk.get("severity", "low")
            
            # Determine which systems this patch applies to
            target_systems = self._select_target_systems(risk_score, severity)
            
            for system in target_systems:
                scheduled_patch = {
                    **patch_risk,  # Copy all original patch risk data
                    "target_system": system,
                    "scheduled_time": self._calculate_schedule_time(system, risk_score),
                    "estimated_duration": self._estimate_duration(severity),
                    "prerequisites": self._generate_prerequisites(system),
                    "rollback_plan": self._generate_rollback_plan(system)
                }
                scheduled_patches.append(scheduled_patch)
        
        return scheduled_patches
    
    def _select_target_systems(self, risk_score: int, severity: str) -> List[Dict]:
        """Select which systems a patch should be applied to"""
        # For PoC: simulate patch applicability logic
        if severity in ["critical", "high"]:
            # Critical patches apply to all production systems
            return [sys for sys in self.systems["systems"] 
                   if sys["environment"] in ["production", "staging"]]
        elif severity == "medium":
            # Medium patches to production and staging
            return [sys for sys in self.systems["systems"]
                   if sys["environment"] in ["production", "staging"]]
        else:
            # Low severity patches start with dev/staging
            return [sys for sys in self.systems["systems"]
                   if sys["environment"] in ["development", "staging"]]
    
    def _calculate_schedule_time(self, system: Dict, risk_score: int) -> str:
        """Calculate when to schedule the patch based on system and risk"""
        base_time = datetime.now()
        
        # Higher risk = sooner scheduling
        if risk_score >= 80:
            # Critical: within 24 hours
            schedule_time = base_time + timedelta(hours=random.randint(1, 24))
        elif risk_score >= 60:
            # High: within 72 hours  
            schedule_time = base_time + timedelta(hours=random.randint(24, 72))
        else:
            # Medium/Low: within a week
            schedule_time = base_time + timedelta(days=random.randint(1, 7))
            
        return schedule_time.isoformat()
    
    def _estimate_duration(self, severity: str) -> str:
        """Estimate patch installation duration"""
        duration_map = {
            "critical": "2-4 hours",
            "high": "1-3 hours", 
            "medium": "30-60 minutes",
            "low": "15-30 minutes"
        }
        return duration_map.get(severity, "30-60 minutes")
    
    def _generate_prerequisites(self, system: Dict) -> List[str]:
        """Generate mock prerequisites for system patching"""
        base_prereqs = [
            "Verify system backup completed",
            "Confirm maintenance window availability",
            "Notify stakeholders of scheduled maintenance"
        ]
        
        if system["criticality"] == "critical":
            base_prereqs.extend([
                "Coordinate with database team",
                "Prepare rollback database snapshot",
                "Schedule on-call engineer availability"
            ])
        elif system["environment"] == "production":
            base_prereqs.extend([
                "Test patch in staging environment",
                "Verify monitoring alerts are active"
            ])
            
        return base_prereqs
    
    def _generate_rollback_plan(self, system: Dict) -> Dict:
        """Generate mock rollback plan for the system"""
        return {
            "method": "automated_snapshot" if system["type"] == "database" else "package_rollback",
            "estimated_rollback_time": "15-30 minutes",
            "rollback_triggers": [
                "Service unavailability > 5 minutes",
                "Error rate > 5%",
                "Manual operator decision"
            ],
            "validation_steps": [
                "Verify service startup",
                "Check application health endpoints", 
                "Validate core functionality"
            ]
        }
    
    def run(self, patch_risks: List[Dict]) -> List[Dict]:
        """Main method to schedule patches"""
        print("[PatchSchedulerAgent] Mapping patches to systems...")
        scheduled_patches = self.map_patches_to_systems(patch_risks)
        print(f"[PatchSchedulerAgent] Scheduled {len(scheduled_patches)} patch deployments")
        return scheduled_patches
