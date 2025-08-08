import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_flow():
    # 1. Create a minimal test plan
    test_plan = {
        "audit_id": "test-plan-001",
        "scheduled_patches": [
            {
                "cve_id": "CVE-2025-12345",
                "target_system": {"name": "Samsung-Ubuntu"},
                "risk_score": 80,
                "severity": "high"
            }
        ],
        "plan_metadata": {
            "generated_at": "2025-08-08T10:00:00",
            "compliance_summary": {"frameworks_involved": []}
        }
    }

    # 2. Submit plan (creates approval)
    print("Submitting patch plan...")
    resp = requests.post(f"{BASE_URL}/patch-plan", json={"patch_plan": test_plan})
    data = resp.json()
    approval_id = data["approval_id"]
    print(f"✅ Approval ID: {approval_id}")

    # 3. Approve the plan (CORRECT SCHEMA)
    print("✅ Approving plan...")
    approve_resp = requests.post(
        f"{BASE_URL}/api/approval/{approval_id}/decision",
        json={
            "decision": "approved",
            "approver": "admin",
            "comments": "Test approval"
        }
    )
    
    if approve_resp.status_code == 422:
        print("❌ Schema error:", approve_resp.json())
        return
    
    print(f"🟢 Approval status: {approve_resp.status_code}")

    # 4. Execute patches
    print("🚀 Executing patches...")
    exec_resp = requests.post(
        f"{BASE_URL}/api/execute/",
        json={"approval_id": approval_id}
    )
    
    if exec_resp.status_code == 500:
        print("❌ Execution error:", exec_resp.text)
    else:
        print(f"🎯 Execution response: {exec_resp.json()}")

if __name__ == "__main__":
    test_full_flow()