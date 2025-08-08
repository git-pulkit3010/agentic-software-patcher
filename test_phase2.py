# backend/test_phase2.py

from agents.patch_scheduler import PatchSchedulerAgent
from agents.auditor import AuditorAgent
import json

def test_phase2_components():
    """Test Phase 2 components independently"""
    
    print("=== Testing Phase 2 Components ===\n")
    
    # Mock patch risks from Phase 1
    mock_patch_risks = [
        {
            "cve_id": "CVE-2024-0001",
            "severity": "critical",
            "risk_score": 95,
            "dependency_risk": "high",
            "rollback_difficulty": "hard",
            "llm_reasoning": "Critical remote code execution vulnerability"
        },
        {
            "cve_id": "CVE-2024-0002", 
            "severity": "high",
            "risk_score": 78,
            "dependency_risk": "medium",
            "rollback_difficulty": "moderate",
            "llm_reasoning": "Privilege escalation vulnerability in authentication system"
        },
        {
            "cve_id": "CVE-2024-0003",
            "severity": "medium",
            "risk_score": 45,
            "dependency_risk": "low", 
            "rollback_difficulty": "easy",
            "llm_reasoning": "Information disclosure vulnerability with limited impact"
        }
    ]
    
    # Test Patch Scheduler
    print("1. Testing Patch Scheduler Agent...")
    scheduler = PatchSchedulerAgent()
    scheduled_patches = scheduler.run(mock_patch_risks)
    print(f"   ✅ Scheduled {len(scheduled_patches)} patch deployments")
    
    # Test Auditor
    print("\n2. Testing Auditor Agent...")
    auditor = AuditorAgent()
    final_plan = auditor.run(scheduled_patches)
    print(f"   ✅ Tagged patches with compliance metadata")
    print(f"   ✅ Audit ID: {final_plan.get('audit_id', 'N/A')}")
    
    # Display sample results
    print(f"\n3. Sample Results:")
    if final_plan.get('scheduled_patches'):
        sample_patch = final_plan['scheduled_patches'][0]
        print(f"   CVE: {sample_patch.get('cve_id')}")
        print(f"   Target System: {sample_patch.get('target_system', {}).get('name')}")
        print(f"   Scheduled Time: {sample_patch.get('scheduled_time')}")
        print(f"   Compliance Frameworks: {sample_patch.get('compliance_metadata', {}).get('applicable_frameworks', [])}")
        print(f"   Prerequisites: {len(sample_patch.get('prerequisites', []))} items")
    
    # Save test results
    with open("backend/data/phase2_test_results.json", "w") as f:
        json.dump(final_plan, f, indent=2)
    print(f"\n💾 Test results saved to: backend/data/phase2_test_results.json")

if __name__ == "__main__":
    test_phase2_components()
